"""
Compute total cost of sales from a price catalogue and sales record.

This module reads a JSON price catalogue and a JSON sales record,
computes the total cost for all sales, and outputs results to the
console and to SalesResults.txt. Invalid data is reported but
execution continues.
"""
# pylint: disable=invalid-name  # Req4: program name must be computeSales.py

import json
import sys
import time

OUTPUT_FILENAME = "SalesResults.txt"


def load_json_file(filepath):
    """
    Load and parse a JSON file. Returns (data, None) on success
    or (None, error_message) on failure.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"Error: File '{filepath}' not found."
    except json.JSONDecodeError as e:
        return None, f"Error: Invalid JSON in '{filepath}': {e}"
    except (IOError, OSError) as e:
        return None, f"Error reading '{filepath}': {e}"


def build_price_map(catalogue_data, errors):
    """
    Build a product name -> price mapping from catalogue data.
    Expects a list of objects with 'title' and 'price' keys.
    Appends error messages to the errors list.
    """
    price_map = {}
    if not isinstance(catalogue_data, list):
        errors.append("Catalogue must be a JSON array of products.")
        return price_map

    for idx, entry in enumerate(catalogue_data):
        if not isinstance(entry, dict):
            errors.append(
                f"Catalogue entry {idx}: expected object, got invalid type."
            )
            continue
        title = entry.get("title")
        price = entry.get("price")
        if title is None or price is None:
            errors.append(
                f"Catalogue entry {idx}: missing 'title' or 'price'."
            )
            continue
        try:
            price_float = float(price)
            if price_float < 0:
                errors.append(
                    f"Catalogue entry {idx}: negative price for '{title}'."
                )
                continue
            price_map[str(title).strip()] = price_float
        except (TypeError, ValueError):
            errors.append(
                f"Catalogue entry {idx}: invalid price for '{title}'."
            )

    return price_map


def compute_sale_total(items, price_map, sale_index, errors):
    """
    Compute total cost for one sale. Items must be a list of
    objects with 'product' and 'quantity'. Returns (total, item_count).
    """
    total = 0.0
    item_count = 0
    if not isinstance(items, list):
        errors.append(f"Sale {sale_index}: 'items' must be an array.")
        return total, item_count

    for idx, line_item in enumerate(items):
        if not isinstance(line_item, dict):
            errors.append(f"Sale {sale_index}, item {idx}: expected object.")
            continue
        product = line_item.get("product")
        quantity = line_item.get("quantity")
        if product is None or quantity is None:
            errors.append(
                f"Sale {sale_index}, item {idx}: missing 'product' or "
                "'quantity'."
            )
            continue
        try:
            qty = int(quantity)
            if qty < 0:
                errors.append(
                    f"Sale {sale_index}, item {idx}: negative quantity for "
                    f"'{product}'."
                )
                continue
        except (TypeError, ValueError):
            errors.append(
                f"Sale {sale_index}, item {idx}: invalid quantity for "
                f"'{product}'."
            )
            continue

        product_key = str(product).strip()
        if product_key not in price_map:
            errors.append(
                f"Sale {sale_index}, item {idx}: product '{product}' "
                "not in catalogue."
            )
            continue

        total += price_map[product_key] * qty
        item_count += 1

    return total, item_count


def compute_all_sales(sales_data, price_map, errors):
    """
    Compute total cost for all sales. Expects a list of sales,
    each with an 'items' array. Returns list of (sale_index, total).
    """
    results = []
    if not isinstance(sales_data, list):
        errors.append("Sales record must be a JSON array of sales.")
        return results

    for sale_index, sale in enumerate(sales_data):
        if not isinstance(sale, dict):
            errors.append(
                f"Sale {sale_index}: expected object, got invalid type."
            )
            continue
        items = sale.get("items")
        if items is None:
            errors.append(
                f"Sale {sale_index}: missing 'items'."
            )
            continue
        sale_total, _ = compute_sale_total(
            items, price_map, sale_index, errors
        )
        results.append((sale_index, sale_total))

    return results


def format_currency(value):
    """Format a number as currency with two decimal places."""
    return f"{value:.2f}"


def print_and_write_results(
    sale_results, grand_total, elapsed_time, errors, output_path
):
    """Print results to console and write the same to output file."""
    lines = []
    lines.append("=" * 60)
    lines.append("SALES RESULTS")
    lines.append("=" * 60)
    lines.append("")

    if errors:
        lines.append(
            "WARNINGS / INVALID DATA (execution continued):"
        )
        lines.append("-" * 60)
        for err in errors:
            lines.append(f"  - {err}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    lines.append("SALE BREAKDOWN")
    lines.append("-" * 60)
    for sale_index, total in sale_results:
        lines.append(f"  Sale #{sale_index}: {format_currency(total)}")
    lines.append("-" * 60)
    lines.append(f"GRAND TOTAL: {format_currency(grand_total)}")
    lines.append("")
    lines.append("=" * 60)
    lines.append(f"Elapsed time: {elapsed_time:.6f} seconds")
    lines.append("=" * 60)

    text = "\n".join(lines)

    print(text)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
    except (IOError, OSError) as e:
        print(f"Error writing results to '{output_path}': {e}")


def main():
    """Main entry: load files, compute sales total, output results."""
    if len(sys.argv) != 3:
        print(
            "Usage: python computeSales.py priceCatalogue.json "
            "salesRecord.json"
        )
        sys.exit(1)

    catalogue_path = sys.argv[1]
    sales_path = sys.argv[2]

    start_time = time.time()
    errors = []

    catalogue_data, load_err = load_json_file(catalogue_path)
    if load_err:
        print(load_err)
        sys.exit(1)

    sales_data, load_err = load_json_file(sales_path)
    if load_err:
        print(load_err)
        sys.exit(1)

    price_map = build_price_map(catalogue_data, errors)
    if not price_map:
        print("No valid products in catalogue. Cannot compute sales.")
        sys.exit(1)

    sale_results = compute_all_sales(sales_data, price_map, errors)
    grand_total = sum(total for _, total in sale_results)
    elapsed_time = time.time() - start_time

    print_and_write_results(
        sale_results, grand_total, elapsed_time, errors, OUTPUT_FILENAME
    )


if __name__ == "__main__":
    main()
