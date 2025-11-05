"""
Function Storage Module
Manages storage, versioning, and retrieval of generated policy functions.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class FunctionStorage:
    """Manages storage and versioning of generated policy functions"""

    def __init__(self, storage_dir: str = "generated"):
        """
        Initialize function storage

        Args:
            storage_dir: Directory to store generated functions
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True, parents=True)

        # Create subdirectories
        self.functions_dir = self.storage_dir / "functions"
        self.versions_dir = self.storage_dir / "versions"
        self.metadata_dir = self.storage_dir / "metadata"

        for directory in [self.functions_dir, self.versions_dir, self.metadata_dir]:
            directory.mkdir(exist_ok=True, parents=True)

    def save_function(
        self,
        company_id: str,
        function_code: str,
        metadata: Dict[str, Any],
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save a generated function with versioning

        Args:
            company_id: Unique company identifier
            function_code: Generated Python code
            metadata: Policy metadata
            version: Version string (auto-generated if not provided)

        Returns:
            Dictionary with save information
        """
        # Generate version if not provided
        if not version:
            version = self._generate_version(company_id)

        # Generate code hash for integrity checking
        code_hash = self._hash_code(function_code)

        # Save current version
        current_file = self.functions_dir / f"{company_id}.py"
        with open(current_file, 'w') as f:
            f.write(function_code)

        # Save versioned copy
        version_file = self.versions_dir / f"{company_id}_v{version}.py"
        with open(version_file, 'w') as f:
            f.write(function_code)

        # Save metadata
        metadata_info = {
            "company_id": company_id,
            "version": version,
            "created_at": datetime.now().isoformat(),
            "code_hash": code_hash,
            "metadata": metadata,
            "file_path": str(current_file),
            "version_path": str(version_file)
        }

        metadata_file = self.metadata_dir / f"{company_id}_v{version}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata_info, f, indent=2)

        # Update version history
        self._update_version_history(company_id, metadata_info)

        return {
            "success": True,
            "company_id": company_id,
            "version": version,
            "file_path": str(current_file),
            "version_path": str(version_file),
            "code_hash": code_hash
        }

    def load_function(
        self,
        company_id: str,
        version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load a generated function

        Args:
            company_id: Company identifier
            version: Specific version to load (latest if not provided)

        Returns:
            Dictionary with function code and metadata, or None if not found
        """
        if version:
            # Load specific version
            version_file = self.versions_dir / f"{company_id}_v{version}.py"
            metadata_file = self.metadata_dir / f"{company_id}_v{version}.json"
        else:
            # Load latest version
            version_file = self.functions_dir / f"{company_id}.py"
            # Get latest metadata
            history = self._get_version_history(company_id)
            if not history:
                return None
            latest = history[-1]
            metadata_file = self.metadata_dir / f"{company_id}_v{latest['version']}.json"

        if not version_file.exists():
            return None

        # Load code
        with open(version_file, 'r') as f:
            code = f.read()

        # Load metadata
        metadata = {}
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

        return {
            "code": code,
            "metadata": metadata,
            "company_id": company_id,
            "version": metadata.get("version", "unknown")
        }

    def list_companies(self) -> List[str]:
        """
        List all companies with stored functions

        Returns:
            List of company IDs
        """
        companies = set()
        for file in self.functions_dir.glob("*.py"):
            companies.add(file.stem)
        return sorted(list(companies))

    def get_version_history(self, company_id: str) -> List[Dict[str, Any]]:
        """
        Get version history for a company

        Args:
            company_id: Company identifier

        Returns:
            List of version metadata dictionaries
        """
        return self._get_version_history(company_id)

    def delete_function(self, company_id: str, version: Optional[str] = None) -> bool:
        """
        Delete a function (version or all versions)

        Args:
            company_id: Company identifier
            version: Specific version to delete (all if not provided)

        Returns:
            True if successful
        """
        if version:
            # Delete specific version
            version_file = self.versions_dir / f"{company_id}_v{version}.py"
            metadata_file = self.metadata_dir / f"{company_id}_v{version}.json"

            if version_file.exists():
                version_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
        else:
            # Delete all versions
            current_file = self.functions_dir / f"{company_id}.py"
            if current_file.exists():
                current_file.unlink()

            # Delete all versioned files
            for file in self.versions_dir.glob(f"{company_id}_v*.py"):
                file.unlink()
            for file in self.metadata_dir.glob(f"{company_id}_v*.json"):
                file.unlink()

            # Delete history
            history_file = self.metadata_dir / f"{company_id}_history.json"
            if history_file.exists():
                history_file.unlink()

        return True

    def import_function(self, company_id: str, version: Optional[str] = None):
        """
        Import a stored function as a Python module

        Args:
            company_id: Company identifier
            version: Version to import (latest if not provided)

        Returns:
            Imported module
        """
        import importlib.util

        function_data = self.load_function(company_id, version)
        if not function_data:
            raise ValueError(f"Function not found: {company_id}")

        # Write to temp file and import
        temp_file = self.storage_dir / f"_temp_{company_id}.py"
        with open(temp_file, 'w') as f:
            f.write(function_data['code'])

        spec = importlib.util.spec_from_file_location(
            f"policy_{company_id}",
            temp_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Clean up temp file
        temp_file.unlink()

        return module

    def _generate_version(self, company_id: str) -> str:
        """Generate next version number"""
        history = self._get_version_history(company_id)
        if not history:
            return "1.0.0"

        # Parse last version and increment
        last_version = history[-1]['version']
        parts = last_version.split('.')
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

        # Increment patch version
        patch += 1

        return f"{major}.{minor}.{patch}"

    def _hash_code(self, code: str) -> str:
        """Generate hash of code for integrity checking"""
        return hashlib.sha256(code.encode()).hexdigest()[:16]

    def _update_version_history(
        self,
        company_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Update version history file"""
        history_file = self.metadata_dir / f"{company_id}_history.json"

        history = []
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)

        history.append({
            "version": metadata["version"],
            "created_at": metadata["created_at"],
            "code_hash": metadata["code_hash"]
        })

        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def _get_version_history(self, company_id: str) -> List[Dict[str, Any]]:
        """Get version history from file"""
        history_file = self.metadata_dir / f"{company_id}_history.json"

        if not history_file.exists():
            return []

        with open(history_file, 'r') as f:
            return json.load(f)


class FunctionRegistry:
    """Registry for tracking and discovering policy functions"""

    def __init__(self, storage: FunctionStorage):
        self.storage = storage

    def register_functions(self, company_id: str, module) -> Dict[str, Any]:
        """
        Register all functions from a module

        Args:
            company_id: Company identifier
            module: Imported policy module

        Returns:
            Dictionary of registered functions
        """
        if hasattr(module, 'get_available_functions'):
            functions = module.get_available_functions()

            registry = {
                "company_id": company_id,
                "registered_at": datetime.now().isoformat(),
                "functions": functions
            }

            # Save registry
            registry_file = self.storage.metadata_dir / f"{company_id}_registry.json"
            with open(registry_file, 'w') as f:
                json.dump(registry, f, indent=2)

            return registry

        return {"error": "Module does not have get_available_functions()"}

    def get_registry(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get function registry for a company"""
        registry_file = self.storage.metadata_dir / f"{company_id}_registry.json"

        if not registry_file.exists():
            return None

        with open(registry_file, 'r') as f:
            return json.load(f)

    def search_functions(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search for functions by keyword

        Args:
            keyword: Search keyword

        Returns:
            List of matching functions from all companies
        """
        results = []
        for company_id in self.storage.list_companies():
            registry = self.get_registry(company_id)
            if registry and 'functions' in registry:
                for func in registry['functions']:
                    if (keyword.lower() in func['name'].lower() or
                        keyword.lower() in func['description'].lower()):
                        results.append({
                            "company_id": company_id,
                            **func
                        })

        return results
