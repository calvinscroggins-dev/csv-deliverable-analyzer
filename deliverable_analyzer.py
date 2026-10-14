"""Summarize a deliverables CSV. Uses only the Python standard library."""
import argparse
import csv
from collections import Counter
from datetime import date
from pathlib import Path


def analyze(path):
    """Validate each record and classify completed delivery timeliness."""
    counts = Counter()
    seen = set()
    with path.open(newline='', encoding='utf-8-sig') as source:
        reader = csv.DictReader(source)
        required = {'id', 'title', 'due_date', 'completed_date'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('Required columns: id, title, due_date, completed_date')
        for line, row in enumerate(reader, start=2):
            if not any(row.values()):
                continue
            identifier = (row.get('id') or '').strip()
            if not identifier or not (row.get('title') or '').strip():
                raise ValueError(f'Row {line}: id and title are required')
            if identifier in seen:
                raise ValueError(f'Row {line}: duplicate id {identifier}')
            seen.add(identifier)
            try:
                due_text = (row.get('due_date') or '').strip()
                done_text = (row.get('completed_date') or '').strip()
                due = date.fromisoformat(due_text) if due_text else None
                done = date.fromisoformat(done_text) if done_text else None
            except ValueError as error:
                raise ValueError(f'Row {line}: dates must use YYYY-MM-DD') from error
            counts['total'] += 1
            counts['completed' if done else 'open'] += 1
            if due is None:
                counts['no_due'] += 1
            if done and due:
                category = 'early' if done < due else 'late' if done > due else 'on_time'
                counts[category] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description='Summarize delivery status and timeliness.')
    parser.add_argument('csv_file', nargs='?', type=Path,
                        default=Path(__file__).with_name('sample_deliverables.csv'))
    args = parser.parse_args()
    try:
        counts = analyze(args.csv_file)
    except (OSError, ValueError, csv.Error) as error:
        parser.exit(1, f'Error: {error}\n')
    print('DELIVERABLE ANALYSIS REPORT')
    print(f'File: {args.csv_file.name}')
    print('-' * 40)
    labels = [('total', 'Total deliverables'), ('completed', 'Completed'),
              ('open', 'Open'), ('early', 'Delivered early'),
              ('on_time', 'Delivered on time'), ('late', 'Delivered late'),
              ('no_due', 'No due date')]
    for key, label in labels:
        print(f'{label:<25} {counts[key]:>3}')
    rate = counts['completed'] / counts['total'] * 100 if counts['total'] else 0
    print(f'Completion rate: {rate:.1f}%')
    print('\nNote: No due date can overlap Completed or Open.')
    print('Timeliness includes only completed items with a due date.')


if __name__ == '__main__':
    main()
