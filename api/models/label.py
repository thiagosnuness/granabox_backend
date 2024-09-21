from api import db


class Label(db.Model):
    """
    Model representing a label (category) for financial items such as
    expenses, income, or payments.

    Attributes:
        id (int): Unique identifier for each label, automatically generated.
        name (str): The name of the label (e.g., 'Habitação', 'Saúde').
        is_default (bool): Indicates if the label is a default (True or False).
    """

    __tablename__ = "labels"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    is_default = db.Column(db.Boolean, default=False)

    def to_dict(self):
        """
        Converts the label instance to a dictionary format.

        Returns:
            dict: The label attributes as a dictionary with keys 'id',
                  'name', and 'is_default'.
        """
        return {
            "id": self.id,
            "name": self.name,
            "is_default": self.is_default,
        }
