"""
Risk assessment and gate decision module
"""
from typing import Dict, List
from config.settings import RISK_WEIGHTS, RISK_GATES, COMPLEXITY_THRESHOLD


class RiskAssessor:
    """Assesses risk of code changes and makes gate decisions."""
    
    def __init__(self):
        self.assessments: Dict[str, Dict] = {}
    
    def assess_risk(
        self,
        filename: str,
        original_analysis: Dict,
        change_stats: Dict,
        ai_changes: List[str]
    ) -> Dict:
        """
        Assess the risk level of code changes.
        
        Args:
            filename: Name of the file
            original_analysis: Static analysis of original code
            change_stats: Change statistics from ChangeDetector
            ai_changes: List of changes made by AI
            
        Returns:
            Risk assessment dictionary with score and gate decision
        """
        # Calculate individual risk components
        complexity_risk = self._assess_complexity_risk(original_analysis)
        change_volume_risk = self._assess_change_volume_risk(change_stats)
        critical_function_risk = self._assess_critical_function_risk(ai_changes)
        issue_severity_risk = self._assess_issue_severity_risk(original_analysis)
        
        # Calculate weighted total risk score (0-100)
        total_risk = (
            complexity_risk * RISK_WEIGHTS['complexity_change'] +
            change_volume_risk * RISK_WEIGHTS['lines_changed'] +
            critical_function_risk * RISK_WEIGHTS['critical_functions'] +
            issue_severity_risk * RISK_WEIGHTS['security_issues']
        ) * 100
        
        # Make gate decision
        gate_decision = self._make_gate_decision(total_risk)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            total_risk,
            complexity_risk,
            change_volume_risk,
            original_analysis
        )
        
        assessment = {
            'filename': filename,
            'risk_score': round(total_risk, 2),
            'gate_decision': gate_decision,
            'risk_components': {
                'complexity_risk': round(complexity_risk * 100, 2),
                'change_volume_risk': round(change_volume_risk * 100, 2),
                'critical_function_risk': round(critical_function_risk * 100, 2),
                'issue_severity_risk': round(issue_severity_risk * 100, 2)
            },
            'recommendations': recommendations
        }
        
        self.assessments[filename] = assessment
        return assessment
    
    def _assess_complexity_risk(self, analysis: Dict) -> float:
        """
        Assess risk based on code complexity.
        Returns value between 0 and 1.
        """
        complexity = analysis.get('complexity', {})
        avg_complexity = complexity.get('average', 0)
        high_complexity_count = complexity.get('high_complexity_count', 0)
        
        # Normalize complexity (0 = simple, 1 = very complex)
        complexity_score = min(avg_complexity / 20, 1.0)
        
        # Add penalty for high complexity functions
        high_complexity_penalty = min(high_complexity_count * 0.1, 0.3)
        
        return min(complexity_score + high_complexity_penalty, 1.0)
    
    def _assess_change_volume_risk(self, change_stats: Dict) -> float:
        """
        Assess risk based on the volume of changes.
        Returns value between 0 and 1.
        """
        total_changes = change_stats.get('total_changes', 0)
        original_lines = change_stats.get('original_lines', 1)
        
        # Calculate change ratio
        change_ratio = total_changes / original_lines
        
        # Normalize (0 = no changes, 1 = complete rewrite)
        return min(change_ratio, 1.0)
    
    def _assess_critical_function_risk(self, ai_changes: List[str]) -> float:
        """
        Assess risk based on changes to critical functions.
        Returns value between 0 and 1.
        """
        critical_keywords = [
            'security', 'auth', 'password', 'token', 'database',
            'sql', 'query', 'encrypt', 'decrypt', 'validate'
        ]
        
        critical_change_count = 0
        for change in ai_changes:
            change_lower = change.lower()
            if any(keyword in change_lower for keyword in critical_keywords):
                critical_change_count += 1
        
        # Normalize based on number of changes
        if not ai_changes:
            return 0.0
        
        return min(critical_change_count / len(ai_changes), 1.0)
    
    def _assess_issue_severity_risk(self, analysis: Dict) -> float:
        """
        Assess risk based on severity of issues found.
        Returns value between 0 and 1.
        """
        issues = analysis.get('issues', [])
        
        if not issues:
            return 0.0
        
        severity_scores = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2,
            'info': 0.1
        }
        
        total_severity = sum(
            severity_scores.get(issue.get('severity', 'low'), 0.2)
            for issue in issues
        )
        
        # Normalize by number of issues (average severity)
        avg_severity = total_severity / len(issues)
        
        return min(avg_severity, 1.0)
    
    def _make_gate_decision(self, risk_score: float) -> str:
        """
        Make a gate decision based on risk score.
        
        Returns:
            'PASS', 'WARN', or 'BLOCK'
        """
        if risk_score < RISK_GATES['PASS']:
            return 'PASS'
        elif risk_score < RISK_GATES['WARN']:
            return 'WARN'
        else:
            return 'BLOCK'
    
    def _generate_recommendations(
        self,
        total_risk: float,
        complexity_risk: float,
        change_volume_risk: float,
        analysis: Dict
    ) -> List[str]:
        """Generate recommendations based on risk assessment."""
        recommendations = []
        
        # Risk-based recommendations
        if total_risk < 30:
            recommendations.append("✓ Low risk changes - safe to proceed")
        elif total_risk < 70:
            recommendations.append("⚠ Medium risk changes - additional review recommended")
        else:
            recommendations.append("⛔ High risk changes - thorough review required before deployment")
        
        # Complexity recommendations
        if complexity_risk > 0.7:
            recommendations.append("Consider refactoring high complexity functions")
        
        # Change volume recommendations
        if change_volume_risk > 0.5:
            recommendations.append("Large volume of changes - consider breaking into smaller releases")
        
        # Issue-based recommendations
        issues = analysis.get('issues', [])
        medium_high_issues = [i for i in issues if i.get('severity') in ['medium', 'high', 'critical']]
        if medium_high_issues:
            recommendations.append(f"Address {len(medium_high_issues)} medium/high severity issues")
        
        # Testing recommendations
        if total_risk > 40:
            recommendations.append("Comprehensive testing recommended before deployment")
            recommendations.append("Consider adding additional unit tests for modified functions")
        
        return recommendations
    
    def get_overall_assessment(self) -> Dict:
        """Get overall assessment across all files."""
        if not self.assessments:
            return {}
        
        total_risk = sum(a['risk_score'] for a in self.assessments.values())
        avg_risk = total_risk / len(self.assessments)
        
        gate_counts = {
            'PASS': sum(1 for a in self.assessments.values() if a['gate_decision'] == 'PASS'),
            'WARN': sum(1 for a in self.assessments.values() if a['gate_decision'] == 'WARN'),
            'BLOCK': sum(1 for a in self.assessments.values() if a['gate_decision'] == 'BLOCK')
        }
        
        # Overall decision is the most restrictive
        if gate_counts['BLOCK'] > 0:
            overall_decision = 'BLOCK'
        elif gate_counts['WARN'] > 0:
            overall_decision = 'WARN'
        else:
            overall_decision = 'PASS'
        
        return {
            'files_assessed': len(self.assessments),
            'average_risk_score': round(avg_risk, 2),
            'overall_gate_decision': overall_decision,
            'gate_counts': gate_counts
        }
