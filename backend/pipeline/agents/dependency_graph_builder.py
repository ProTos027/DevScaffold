"""
Dependency Graph Builder - Deterministic graph construction and topological sort.
No LLM involvement.
"""
from typing import List, Set, Dict
from ..schemas import ComponentPlanSchema, DependencyGraphSchema, DependencyEdge


class CyclicDependencyError(Exception):
    """Raised when a cyclic dependency is detected."""
    pass


def build_dependency_graph(component_plan: ComponentPlanSchema) -> DependencyGraphSchema:
    """
    Build dependency graph from Component Plan.
    Performs topological sort and detects cycles.
    
    Args:
        component_plan: ComponentPlanSchema with components and dependencies
    
    Returns:
        DependencyGraphSchema with nodes, edges, and build_order
    
    Raises:
        CyclicDependencyError: If circular dependencies are detected
    """
    # Extract nodes and edges
    nodes = [comp.id for comp in component_plan.components]
    edges = []
    
    # Build dependency edges
    for comp in component_plan.components:
        for dep in comp.depends_on:
            edges.append(DependencyEdge(from_component=comp.id, to_component=dep))
    
    # Perform topological sort (Kahn's algorithm)
    build_order = topological_sort(nodes, edges)
    
    return DependencyGraphSchema(
        nodes=nodes,
        edges=[edge.model_dump(by_alias=True) for edge in edges]
    )


def topological_sort(nodes: List[str], edges: List[DependencyEdge]) -> List[str]:
    """
    Perform topological sort using Kahn's algorithm.
    
    Args:
        nodes: List of node IDs
        edges: List of DependencyEdge objects
    
    Returns:
        List of nodes in dependency order (dependencies first)
    
    Raises:
        CyclicDependencyError: If a cycle is detected
    """
    # Build adjacency list and in-degree map
    adj_list: Dict[str, List[str]] = {node: [] for node in nodes}
    in_degree: Dict[str, int] = {node: 0 for node in nodes}
    
    for edge in edges:
        # Edge from A to B means A depends on B, so B must come before A
        source = edge.from_component
        target = edge.to_component
        adj_list[target].append(source)
        in_degree[source] += 1
    
    # Find nodes with no incoming edges (no dependencies)
    queue = [node for node in nodes if in_degree[node] == 0]
    result = []
    
    while queue:
        # Remove node from queue
        current = queue.pop(0)
        result.append(current)
        
        # For each node that depends on current
        for neighbor in adj_list[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # If not all nodes are processed, there's a cycle
    if len(result) != len(nodes):
        # Find nodes in cycle
        cycle_nodes = [node for node in nodes if in_degree[node] > 0]
        raise CyclicDependencyError(
            f"Cyclic dependency detected among components: {', '.join(cycle_nodes)}"
        )
    
    return result


def detect_cycles(nodes: List[str], edges: List[Dict]) -> List[List[str]]:
    """
    Detect all cycles in the dependency graph (if any).
    
    Args:
        nodes: List of node IDs
        edges: List of edge dicts with 'from' and 'to' keys
    
    Returns:
        List of cycles (each cycle is a list of nodes)
    """
    # Build adjacency list
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
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)
        
        rec_stack.remove(node)
    
    for node in nodes:
        if node not in visited:
            dfs(node, [])
    
    return cycles
