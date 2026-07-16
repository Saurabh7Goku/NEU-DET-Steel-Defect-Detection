#!/usr/bin/env python
"""NEU-DET Steel Surface Defect Detection — CLI entry point.

Usage:
    python main.py train --model fpn_resnet
    python main.py train --model unet_resnet --epochs 30 --lr 1e-4
    python main.py evaluate --model fpn_resnet --checkpoint checkpoints/model_fpn_resnet.pth
    python main.py export --model fpn_resnet --checkpoint checkpoints/model_fpn_resnet.pth
"""

import argparse
import sys


def cmd_train(args):
    from src.models import MODEL_REGISTRY
    import importlib

    model_name = args.model
    module_name = {
        "fpn_resnet": "src.models.fpn_resnet",
        "fpn_inceptionv4": "src.models.fpn_inceptionv4",
        "fpn_xception": "src.models.fpn_xception",
        "unet_resnet": "src.models.unet_resnet",
    }[model_name]

    mod = importlib.import_module(module_name)
    print(f"Training model: {model_name}")
    trainer = mod.train(epochs=args.epochs, lr=args.lr, checkpoint_path=args.checkpoint)

    if args.plot:
        from src.utils.visualization import plot_training_curves
        save_path = args.plot if isinstance(args.plot, str) else f"training_curves_{model_name}.png"
        plot_training_curves(trainer, save_path=save_path)

    return trainer


def cmd_evaluate(args):
    from src.evaluation.evaluator import evaluate
    results = evaluate(args.model, args.checkpoint, batch_size=args.batch_size)
    return results


def cmd_export(args):
    from src.utils.onnx_export import export_to_onnx
    export_to_onnx(args.model, args.checkpoint, args.output)


def interactive_menu():
    """Fallback interactive menu when no subcommand is given."""
    print("=" * 60)
    print("  NEU-DET Steel Surface Defect Detection")
    print("=" * 60)
    print("\n  Available models:")
    print("    1. fpn_resnet       — FPN + ResNet-34")
    print("    2. fpn_inceptionv4  — FPN + InceptionV4")
    print("    3. fpn_xception     — FPN + Xception")
    print("    4. unet_resnet      — UNet + ResNet-34")
    print()

    choice = input("  Select model (1-4): ").strip()
    model_map = {"1": "fpn_resnet", "2": "fpn_inceptionv4", "3": "fpn_xception", "4": "unet_resnet"}
    model = model_map.get(choice)
    if not model:
        print("  Invalid choice.")
        sys.exit(1)

    action = input("  Action — (t)rain, (e)valuate, (x)port ONNX: ").strip().lower()
    if action == "t":
        epochs = input("  Epochs [20]: ").strip()
        epochs = int(epochs) if epochs else 20
        lr = input("  Learning rate [5e-4]: ").strip()
        lr = float(lr) if lr else 5e-4
        print(f"\n  Starting training: {model} for {epochs} epochs at lr={lr}")
        args = argparse.Namespace(model=model, epochs=epochs, lr=lr, checkpoint=None, plot=True)
        cmd_train(args)
    elif action == "e":
        ckpt = input(f"  Checkpoint path [checkpoints/model_{model}.pth]: ").strip()
        ckpt = ckpt or f"checkpoints/model_{model}.pth"
        args = argparse.Namespace(model=model, checkpoint=ckpt, batch_size=2)
        cmd_evaluate(args)
    elif action == "x":
        ckpt = input(f"  Checkpoint path [checkpoints/model_{model}.pth]: ").strip()
        ckpt = ckpt or f"checkpoints/model_{model}.pth"
        args = argparse.Namespace(model=model, checkpoint=ckpt, output=None)
        cmd_export(args)
    else:
        print("  Invalid action.")


def main():
    parser = argparse.ArgumentParser(
        description="NEU-DET Steel Surface Defect Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # train
    p_train = subparsers.add_parser("train", help="Train a segmentation model")
    p_train.add_argument("--model", required=True, choices=["fpn_resnet", "fpn_inceptionv4", "fpn_xception", "unet_resnet"])
    p_train.add_argument("--epochs", type=int, default=20)
    p_train.add_argument("--lr", type=float, default=5e-4)
    p_train.add_argument("--checkpoint", default=None, help="Resume from checkpoint path")
    p_train.add_argument("--plot", nargs="?", const=True, default=False, help="Save training curves plot")
    p_train.set_defaults(func=cmd_train)

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Evaluate a trained model")
    p_eval.add_argument("--model", required=True, choices=["fpn_resnet", "fpn_inceptionv4", "fpn_xception", "unet_resnet"])
    p_eval.add_argument("--checkpoint", required=True)
    p_eval.add_argument("--batch-size", type=int, default=2)
    p_eval.set_defaults(func=cmd_evaluate)

    # export
    p_export = subparsers.add_parser("export", help="Export model to ONNX")
    p_export.add_argument("--model", required=True, choices=["fpn_resnet", "fpn_inceptionv4", "fpn_xception", "unet_resnet"])
    p_export.add_argument("--checkpoint", required=True)
    p_export.add_argument("--output", default=None)
    p_export.set_defaults(func=cmd_export)

    args = parser.parse_args()

    if args.command is None:
        interactive_menu()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
