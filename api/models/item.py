from datetime import datetime

from api import db


class Item(db.Model):
    """
    Model representing a financial item such as expenses, income, or payments.

    Attributes:
        id (int): Unique identifier for each item, automatically generated.
        recurrence_id (str): Unique identifier for a series of recurring items.
        recurrence (str): Recurrence of the item ('Única' or 'Mensal').
        months (int): The number of recurring months (if applicable).
        type (str): Status of the item ('A pagar', 'Pago', 'Rendimentos').
        description (str): A brief description of the item.
        amount (float): The monetary value of the item.
        due_date (date): The due date of the item in the format YYYY-MM-DD.
        due_status (str):The due status('VENCIDO', 'VENCE HOJE', 'A VENCER').
        transaction_date (datetime): The date and time when the item was
        created or last modified.
        label_id (int): Foreign key referencing the associated label.
        label (Label): Relationship to the Label model that categorizes item.
    """

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    recurrence_id = db.Column(db.String(36), nullable=True)
    recurrence = db.Column(db.String(20), nullable=False)
    months = db.Column(db.Integer, nullable=True)
    type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    due_status = db.Column(db.String(50), nullable=True)
    transaction_date = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )

    # Foreign key to link Label and Item
    label_id = db.Column(db.Integer, db.ForeignKey("labels.id"))
    label = db.relationship("Label", backref="items")

    def to_dict(self):
        """
        Converts the Item instance into a dictionary format.

        Returns:
            dict: The item attributes as a dictionary with keys 'id',
                  'recurrence_id', 'recurrence', 'months', 'type',
                  'description', 'amount', 'due_date', 'due_status',
                  'transaction_date', and 'label'.
        """
        return {
            "id": self.id,
            "recurrence_id": self.recurrence_id,
            "recurrence": self.recurrence,
            "months": self.months,
            "type": self.type,
            "description": self.description,
            "amount": self.amount,
            "due_date": self.due_date.strftime("%Y-%m-%d"),
            "due_status": self.due_status,
            "transaction_date": self.transaction_date.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "label": self.label.name if self.label else None,
            "label_id": self.label_id,
        }
