"""
Graph utilities for the DevScaffold pipeline.
Deterministic logic for dependency management and topological sorting.
"""
from typing import List, Dict, Set
from ..schemas import ComponentPlanSchema, DependencyEdge, CyclicDependencyError


def sort_component_plan_in_place(
    component_plan: ComponentPlanSchema
) -> None:
    """
    Sorts the components list inside ComponentPlanSchema in-place
    using topological sort and detects cycles.
    """
    nodes = [comp.id for comp in component_plan.components]
    edges = []
    
    for comp in component_plan.components:
        for dep in comp.depends_on:
            edges.append(DependencyEdge(from_component=comp.id, to_component=dep))
    
    build_order = topological_sort(nodes, edges)

    comp_map = {comp.id: comp for comp in component_plan.components}
    component_plan.components = [comp_map[node] for node in build_order]


def topological_sort(nodes: List[str], edges: List[DependencyEdge]) -> List[str]:
    """Perform topological sort using Kahn's algorithm."""
    adj_list: Dict[str, List[str]] = {node: [] for node in nodes}
    in_degree: Dict[str, int] = {node: 0 for node in nodes}
    
    for edge in edges:
        source = edge.from_component
        target = edge.to_component
        adj_list[target].append(source)
        in_degree[source] += 1
    
    queue = [node for node in nodes if in_degree[node] == 0]
    result = []
    
    while queue:
        current = queue.pop(0)
        result.append(current)
        
        for neighbor in adj_list[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(result) != len(nodes):
        cycles = detect_cycles(nodes, [
            {'from': edge.from_component, 'to': edge.to_component} 
            for edge in edges
        ])
        if cycles:
            cycle_desc = " | ".join([" → ".join(c) for c in cycles[:3]])
            raise CyclicDependencyError(f"Cyclic dependency detected: {cycle_desc}")
        
        cycle_nodes = [node for node in nodes if in_degree[node] > 0]
        raise CyclicDependencyError(
            f"Cyclic dependency detected among components: {', '.join(cycle_nodes)}"
        )
    
    return result


def detect_cycles(nodes: List[str], edges: List[Dict]) -> List[List[str]]:
    """Detect all cycles in the dependency graph."""
    adj_list: Dict[str, List[str]] = {node: [] for node in nodes}
    for edge in edges:
        adj_list[edge['from']].append(edge['to'])
    
    visited: Set[str] = set()
    rec_stack: Set[str] = set()
    cycles = []
    
    def dfs(node: str, path: List[str]):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in adj_list.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path.copy())
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
        
        rec_stack.remove(node)
    
    for node in nodes:
        if node not in visited:
            dfs(node, [])
    
    return cycles
