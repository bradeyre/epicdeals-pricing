"""
Research Queue Service
Manages items that need manual repair cost research (2 working day SLA)
"""

from datetime import datetime, timedelta
import json
import os


class ResearchQueueService:
    """
    Handles queue for items requiring manual research
    - Repair costs that couldn't be found automatically
    - Complex items needing expert assessment
    - 2 working day response SLA
    """

    def __init__(self, queue_file='data/research_queue.json'):
        self.queue_file = queue_file
        self._ensure_queue_file()

    def _ensure_queue_file(self):
        """Create queue file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
        if not os.path.exists(self.queue_file):
            with open(self.queue_file, 'w') as f:
                json.dump([], f)

    def add_to_queue(self, product_info, contact_info, unknown_repairs, preliminary_offer):
        """
        Add item to research queue

        Args:
            product_info (dict): Product details
            contact_info (dict): User contact info
            unknown_repairs (list): Issues needing cost research
            preliminary_offer (float): Preliminary offer amount

        Returns:
            dict: Queue entry with ID and SLA deadline
        """

        queue_entry = {
            'id': self._generate_queue_id(),
            'added_date': datetime.now().isoformat(),
            'sla_deadline': self._calculate_sla_deadline(),
            'status': 'pending',
            'product_info': product_info,
            'contact_info': contact_info,
            'unknown_repairs': unknown_repairs,
            'preliminary_offer': preliminary_offer,
            'final_offer': None,
            'research_notes': '',
            'completed_date': None
        }

        # Load current queue
        queue = self._load_queue()
        queue.append(queue_entry)
        self._save_queue(queue)

        return queue_entry

    def get_pending_items(self):
        """Get all pending research items"""
        queue = self._load_queue()
        return [item for item in queue if item['status'] == 'pending']

    def get_overdue_items(self):
        """Get items past SLA deadline"""
        queue = self._load_queue()
        now = datetime.now()

        overdue = []
        for item in queue:
            if item['status'] == 'pending':
                deadline = datetime.fromisoformat(item['sla_deadline'])
                if now > deadline:
                    overdue.append(item)

        return overdue

    def complete_research(self, queue_id, final_offer, research_notes):
        """
        Mark research as completed

        Args:
            queue_id (str): Queue entry ID
            final_offer (float): Final calculated offer
            research_notes (str): Notes from manual research

        Returns:
            dict: Updated queue entry or None if not found
        """

        queue = self._load_queue()

        for item in queue:
            if item['id'] == queue_id:
                item['status'] = 'completed'
                item['final_offer'] = final_offer
                item['research_notes'] = research_notes
                item['completed_date'] = datetime.now().isoformat()

                self._save_queue(queue)
                return item

        return None

    def _generate_queue_id(self):
        """Generate unique queue ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"RQ{timestamp}"

    def _calculate_sla_deadline(self):
        """Calculate 2 working day deadline"""
        now = datetime.now()
        days_added = 0
        current = now

        while days_added < 2:
            current += timedelta(days=1)
            # Skip weekends (5=Saturday, 6=Sunday)
            if current.weekday() < 5:
                days_added += 1

        return current.isoformat()

    def _load_queue(self):
        """Load queue from file"""
        try:
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_queue(self, queue):
        """Save queue to file"""
        with open(self.queue_file, 'w') as f:
            json.dump(queue, f, indent=2)

    def get_stats(self):
        """Get queue statistics"""
        queue = self._load_queue()

        stats = {
            'total_items': len(queue),
            'pending': len([i for i in queue if i['status'] == 'pending']),
            'completed': len([i for i in queue if i['status'] == 'completed']),
            'overdue': len(self.get_overdue_items())
        }

        return stats
