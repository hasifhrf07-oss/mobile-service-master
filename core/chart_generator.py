
"""Chart Generator"""
import os

ROOT = os.path.dirname(os.path.dirname(__file__))


def generate_brand_tree(brand_data):
    """Generate ASCII tree"""
    lines = [f"Brand: {brand_data.get('name', '?')}"]
    for s in brand_data.get("series", []):
        lines.append(f"  - {s}")
    return "\n".join(lines)


def save_all_charts():
    """Save charts"""
    out = os.path.join(ROOT, "data", "charts")
    os.makedirs(out, exist_ok=True)
    return {"chart": out}


if __name__ == "__main__":
    print(save_all_charts())