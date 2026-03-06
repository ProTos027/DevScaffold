"""
Action Logger utility for pipeline agents.
"""
from projects.models import PipelineActionLog


class ActionLogger:
    """Tracks and retrieves agent actions for a specific project's pipeline run."""
    
    def __init__(self, project):
        self.project = project
    
    def log(self, stage: str, agent: str, action: str, details: dict = None):
        """Record an agent action."""
        PipelineActionLog.objects.create(
            project=self.project,
            stage=stage,
            agent=agent,
            action=action,
            details=details or {}
        )
    
    def get_log(self, stage: str = None):
        """Get action logs, optionally filtered by stage."""
        qs = self.project.action_logs.all()
        if stage:
            qs = qs.filter(stage=stage)
        return list(qs.values('stage', 'agent', 'action', 'details'))
    
    def get_summary(self) -> str:
        """
        Returns a structured text summary of all actions for prompt injection.
        """
        logs = self.get_log()
        if not logs:
            return "## PROJECT TIMELINE\nNo previous pipeline actions recorded."
        
        lines = ["## PROJECT TIMELINE (PROCESS HISTORY)"]
        lines.append("> [!NOTE]")
        lines.append("> Below is the chronological sequence of actions taken by other agents. Refer to this to understand the 'why' and context of previous decisions.\n")
        
        for log in logs:
            detail_str = ""
            details = log.get('details', {})
            if details:
                import json
                # 1. Harvest explicit decisions/choices from agents
                decisions = details.get('choices', {})
                decision_items = [f"{k}={json.dumps(v)}" for k, v in decisions.items()]
                
                # 2. Add other scalar facts
                fact_items = [f"{k}: {json.dumps(v)}" for k, v in details.items() if not isinstance(v, (dict, list)) and k != 'choices']
                
                all_facts = decision_items + fact_items
                if all_facts:
                    detail_str = f" - Facts: {', '.join(all_facts[:10])}"
                    
            lines.append(f"- **[{log['stage'].upper()}]** {log['agent']} -> {log['action']}{detail_str}")
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear all action logs for this project (for pipeline reruns)."""
        self.project.action_logs.all().delete()
