    import os
    import copy
    import torch
    import random
    import numpy as np
    import torch.nn as nn
    import torch.optim as optim
    import matplotlib.pyplot as plt
    from sklearn.metrics import confusion_matrix, classification_report
    from torch.utils.data import DataLoader
    from torchvision import datasets, transforms, models

    # =========================================================
    # CONFIG
    # =========================================================
    class Config:
        data_dir = "datasets"
        batch_size = 32
        num_epochs = 30
        lr = 1e-3
        patience = 5
        num_workers = 0   # IMPORTANT for Windows CPU
        seed = 42
        model_path = "best_model.pth"

    cfg = Config()


    # =========================================================
    # Reproducibility
    # =========================================================
    def set_seed(seed):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

    set_seed(cfg.seed)

    device = torch.device("cpu")  # Force CPU for stability


    # =========================================================
    # Data Transforms
    # =========================================================
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(0.2, 0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                            [0.229, 0.224, 0.225])
    ])

    val_test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                            [0.229, 0.224, 0.225])
    ])


    # =========================================================
    # Train & Evaluate Functions
    # =========================================================
    def train_one_epoch(model, loader, optimizer, criterion):
        model.train()
        total_loss, correct, total = 0, 0, 0

        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            _, preds = outputs.max(1)
            total += labels.size(0)
            correct += preds.eq(labels).sum().item()

        return total_loss / len(loader), 100 * correct / total


    def evaluate(model, loader, criterion):
        model.eval()
        total_loss, correct, total = 0, 0, 0

        with torch.no_grad():
            for images, labels in loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                total_loss += loss.item()
                _, preds = outputs.max(1)
                total += labels.size(0)
                correct += preds.eq(labels).sum().item()

        return total_loss / len(loader), 100 * correct / total


    def main():

        # =========================================================
        # Dataset & DataLoader
        # =========================================================
        train_dataset = datasets.ImageFolder(os.path.join(cfg.data_dir, "train"), transform=train_transform)
        val_dataset = datasets.ImageFolder(os.path.join(cfg.data_dir, "val"), transform=val_test_transform)
        test_dataset = datasets.ImageFolder(os.path.join(cfg.data_dir, "test"), transform=val_test_transform)

        train_loader = DataLoader(train_dataset, batch_size=cfg.batch_size,
                                shuffle=True, num_workers=cfg.num_workers)

        val_loader = DataLoader(val_dataset, batch_size=cfg.batch_size,
                                shuffle=False, num_workers=cfg.num_workers)

        test_loader = DataLoader(test_dataset, batch_size=cfg.batch_size,
                                shuffle=False, num_workers=cfg.num_workers)

        class_names = train_dataset.classes
        num_classes = len(class_names)

        print(f"Classes: {class_names}")
        print(f"Training: {len(train_dataset)}, Validation: {len(val_dataset)}, Test: {len(test_dataset)}")

        # =========================================================
        # Model
        # =========================================================
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

        # Freeze backbone
        for param in model.parameters():
            param.requires_grad = False

        model.fc = nn.Linear(model.fc.in_features, num_classes)
        model = model.to(device)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.fc.parameters(), lr=cfg.lr)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", patience=2, factor=0.1)

        # =========================================================
        # Training Loop
        # =========================================================
        best_val_loss = float("inf")
        early_stop_counter = 0

        for epoch in range(cfg.num_epochs):

            train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion)
            val_loss, val_acc = evaluate(model, val_loader, criterion)

            scheduler.step(val_loss)

            print(f"Epoch [{epoch+1}/{cfg.num_epochs}] "
                f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | "
                f"Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}%")

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(model.state_dict(), cfg.model_path)
                early_stop_counter = 0
                print("  → Best model saved")
            else:
                early_stop_counter += 1

            if early_stop_counter >= cfg.patience:
                print("Early stopping triggered")
                break

        # =========================================================
        # Final Evaluation
        # =========================================================
        model.load_state_dict(torch.load(cfg.model_path))

        train_loss, train_acc = evaluate(model, train_loader, criterion)
        val_loss, val_acc = evaluate(model, val_loader, criterion)
        test_loss, test_acc = evaluate(model, test_loader, criterion)

        print("\n========== FINAL RESULTS ==========")
        print(f"Training   -> Loss: {train_loss:.4f} | Accuracy: {train_acc:.2f}%")
        print(f"Validation -> Loss: {val_loss:.4f} | Accuracy: {val_acc:.2f}%")
        print(f"Test       -> Loss: {test_loss:.4f} | Accuracy: {test_acc:.2f}%")
        print("===================================")

        # =========================================================
        # Confusion Matrix
        # =========================================================
        model.eval()
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for images, labels in test_loader:
                images = images.to(device)
                outputs = model(images)
                _, preds = outputs.max(1)

                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.numpy())

        cm = confusion_matrix(all_labels, all_preds)

        print("\nConfusion Matrix:")
        print(cm)

        print("\nClassification Report:")
        print(classification_report(all_labels, all_preds, target_names=class_names))

        # Plot Confusion Matrix
        plt.figure(figsize=(8, 6))
        plt.imshow(cm, interpolation='nearest')
        plt.title("Confusion Matrix")
        plt.colorbar()
        plt.xticks(range(num_classes), class_names, rotation=45)
        plt.yticks(range(num_classes), class_names)
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        plt.show()


    if __name__ == "__main__":
        main()