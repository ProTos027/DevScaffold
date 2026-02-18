"""
Action Logger utility for pipeline agents.
Provides a simple interface for agents to log actions and 
read previous action summaries for pipeline consistency.
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
        Returns a concise text summary of all actions for injection into agent prompts.
        Downstream agents use this to understand what upstream agents decided.
        """
        logs = self.get_log()
        if not logs:
            return "No previous pipeline actions recorded."
        
        lines = []
        for log in logs:
            detail_str = ""
            if log['details']:
                # Compact key details for prompt injection
                key_items = [f"{k}={v}" for k, v in log['details'].items() if not isinstance(v, (dict, list))]
                if key_items:
                    detail_str = f" ({', '.join(key_items[:5])})"
            lines.append(f"[{log['stage']}] {log['agent']}: {log['action']}{detail_str}")
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear all action logs for this project (for pipeline reruns)."""
        self.project.action_logs.all().delete()
