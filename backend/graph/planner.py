from backend.graph.state import ResearchState
from backend.memory.context_manager import context_manager
from backend.models.llm_router import get_router
from backend.models.schemas import MoleculeIdentity
from backend.retrieval.api_client import api_client

async def planner_node(state: ResearchState) -> dict:
    """Resolves Molecule Identity via ChEMBL API and seeds Context"""
    session_id = state["session_id"]
    molecule = state["molecule_name"]
    print(f"[{session_id}] Planner resolving identity for: {molecule}")
    
    from backend.memory.sse_manager import sse_manager
    await sse_manager.emit(session_id, {
        "event": "planner_started",
        "domain": "planner",
        "status": "started",
        "message": f"Resolving molecular identity for {molecule}..."
    })

    # Try ChEMBL API first
    canonical_name = molecule
    aliases = [molecule]
    description = ""
    chembl_id = ""

    try:
        # ChEMBL molecule search - use simpler search endpoint
        response = await api_client.get(
            f"https://www.ebi.ac.uk/chembl/api/data/molecule/search.json",
            params={"q": molecule}
        )
        data = response.json()
        
        if data.get("molecules") and len(data["molecules"]) > 0:
            mol = data["molecules"][0]
            canonical_name = mol.get("pref_name", molecule) or molecule
            chembl_id = mol.get("molecule_chembl_id", "")

            # Get synonyms
            if "molecule_synonyms" in mol:
                aliases = [syn.get("molecule_synonym", "") for syn in mol["molecule_synonyms"][:10]]
                aliases = [a for a in aliases if a]

            # Get description from molecule properties
            if "molecule_properties" in mol:
                props = mol["molecule_properties"]
                description = f"Molecular formula: {props.get('full_molformula', 'N/A')}"

            print(f"[{session_id}] ChEMBL resolved: {canonical_name} | ChEMBL ID: {chembl_id} (aliases: {len(aliases)})")
            
            await sse_manager.emit(session_id, {
                "event": "planner_progress",
                "domain": "planner",
                "status": "started",
                "message": f"Resolved to {canonical_name} (ChEMBL ID: {chembl_id})"
            })
    except Exception as e:
        print(f"[{session_id}] ChEMBL lookup failed: {e}. Using LLM fallback.")
        
        await sse_manager.emit(session_id, {
            "event": "planner_progress",
            "domain": "planner",
            "status": "started",
            "message": f"ChEMBL lookup failed, using AI to resolve identity..."
        })
        
        # Fallback to LLM if ChEMBL fails
        prompt = f"Resolve the canonical name and aliases for the molecule/drug: {molecule}. Output according to MoleculeIdentity schema."
        try:
            identity = await get_router().invoke_extraction(prompt, MoleculeIdentity)
            canonical_name = identity.canonical_name
            aliases = identity.aliases
            description = identity.description
        except Exception as llm_err:
            print(f"[{session_id}] LLM fallback also failed: {llm_err}")
            # Use the original name as fallback
            canonical_name = molecule
    
    # Save to context
    await context_manager.set_session_entity(session_id, {
        "canonical_name": canonical_name,
        "aliases": aliases,
        "description": description,
        "chembl_id": chembl_id
    })
    
    await sse_manager.emit(session_id, {
        "event": "planner_completed",
        "domain": "planner",
        "status": "completed",
        "message": f"Identity resolved: {canonical_name}. Dispatching 4 research agents..."
    })
        
    return {
        "pending_tasks": ["clinical", "patent", "market", "regulatory"],
        "molecule_name": canonical_name
    }
