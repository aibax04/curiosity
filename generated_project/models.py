from datetime import date

class TodoItem:
    def __init__(self, item_text: str, due_date: date, reminder_status: bool = False):
        self.item_text = item_text
        self.due_date = due_date
        self.reminder_status = reminder_status

    def __str__(self):
        return f'TodoItem({self.item_text}, {self.due_date}, {self.reminder_status})'

    def to_dict(self) -> dict:
        return {'item_text': self.item_text, 'due_date': self.due_date.isoformat(), 'reminder_status': self.reminder_status}