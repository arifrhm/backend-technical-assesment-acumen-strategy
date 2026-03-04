import httpx
from sqlalchemy.orm import Session
from models.customer import Customer
from datetime import datetime
from typing import List, Dict


class IngestionService:
    def __init__(self, flask_api_url: str = "http://flask-mock-server:5000"):
        self.flask_api_url = flask_api_url

    async def fetch_all_customers(self) -> List[Dict]:
        """
        Fetch all customers from Flask API with pagination.
        """
        all_customers = []
        page = 1
        limit = 100  # Larger limit to reduce requests

        async with httpx.AsyncClient() as client:
            while True:
                try:
                    response = await client.get(
                        f"{self.flask_api_url}/api/customers",
                        params={"page": page, "limit": limit}
                    )
                    response.raise_for_status()
                    data = response.json()

                    customers = data.get('data', [])
                    if not customers:
                        break

                    all_customers.extend(customers)

                    # Check if we've fetched all customers
                    if len(all_customers) >= data.get('total', 0):
                        break

                    page += 1

                except httpx.HTTPError as e:
                    print(f"Error fetching customers from Flask API: {e}")
                    raise

        return all_customers

    def upsert_customers(self, db: Session, customers: List[Dict]) -> int:
        """
        Upsert customers into database.
        Returns number of records processed.
        """
        records_processed = 0

        for customer_data in customers:
            # Parse date strings
            date_of_birth = None
            if customer_data.get('date_of_birth'):
                try:
                    date_of_birth = datetime.strptime(
                        customer_data['date_of_birth'], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    pass

            created_at = None
            if customer_data.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(
                        customer_data['created_at'].replace('Z', '+00:00')
                    )
                except ValueError:
                    pass

            # Check if customer exists
            existing_customer = db.query(Customer).filter(
                Customer.customer_id == customer_data['customer_id']
            ).first()

            if existing_customer:
                # Update existing customer
                existing_customer.first_name = customer_data.get('first_name')
                existing_customer.last_name = customer_data.get('last_name')
                existing_customer.email = customer_data.get('email')
                existing_customer.phone = customer_data.get('phone')
                existing_customer.address = customer_data.get('address')
                existing_customer.date_of_birth = date_of_birth
                existing_customer.account_balance = customer_data.get('account_balance')
                existing_customer.created_at = created_at
            else:
                # Create new customer
                new_customer = Customer(
                    customer_id=customer_data['customer_id'],
                    first_name=customer_data.get('first_name'),
                    last_name=customer_data.get('last_name'),
                    email=customer_data.get('email'),
                    phone=customer_data.get('phone'),
                    address=customer_data.get('address'),
                    date_of_birth=date_of_birth,
                    account_balance=customer_data.get('account_balance'),
                    created_at=created_at
                )
                db.add(new_customer)

            records_processed += 1

        db.commit()
        return records_processed

    async def ingest_and_save(self, db: Session) -> Dict:
        """
        Fetch customers from Flask API and save to database.
        """
        try:
            # Fetch all customers from Flask API
            customers = await self.fetch_all_customers()

            # Upsert into database
            records_processed = self.upsert_customers(db, customers)

            return {
                "status": "success",
                "records_processed": records_processed
            }
        except Exception as e:
            db.rollback()
            raise e
