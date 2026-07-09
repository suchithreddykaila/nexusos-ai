import React, { useState, useEffect } from "react";
import { useAuthStore } from "../store/auth";
import { useWorkspaceStore } from "../store/workspace";
import { useKnowledgeStore } from "../store/knowledge";
import type { Project, Collection, Folder, KnowledgeAsset } from "../store/knowledge";
import { 
  Folder as FolderIcon, FileText, Plus, ChevronRight, Briefcase, 
  Layers, Star, Trash2, Tag, Search, ArrowLeft, RefreshCw, Eye, Info, Link as LinkIcon
} from "lucide-react";

export const Documents: React.FC = () => {
  const { accessToken } = useAuthStore();
  const { activeWorkspace } = useWorkspaceStore();
  const {
    projects, collections, folders, assets, favorites, recycleBin, timeline, tags,
    activeProject, activeCollection, activeFolder, loading,
    fetchProjects, createProject, fetchCollections, createCollection,
    fetchFolders, createFolder, moveFolder, fetchAssets, createAsset, deleteAsset,
    fetchRecycleBin, restoreItem, permanentDeleteItem, fetchFavorites, toggleFavorite,
    fetchTimeline, fetchTags, createTag, setActiveProject, setActiveCollection, setActiveFolder
  } = useKnowledgeStore();

  const [showRecycleBin, setShowRecycleBin] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<KnowledgeAsset | null>(null);

  // Dialog & Form input states
  const [newProjName, setNewProjName] = useState("");
  const [newProjDesc, setNewProjDesc] = useState("");
  
  const [newColName, setNewColName] = useState("");
  const [newColDesc, setNewColDesc] = useState("");

  const [newFolderName, setNewFolderName] = useState("");
  const [newAssetName, setNewAssetName] = useState("");
  const [newAssetType, setNewAssetType] = useState("document");

  const [searchQuery, setSearchQuery] = useState("");
  const [newTagName, setNewTagName] = useState("");

  // Load baseline workspace projects and tags
  useEffect(() => {
    if (accessToken && activeWorkspace) {
      fetchProjects(accessToken, activeWorkspace.id);
      fetchFavorites(accessToken, activeWorkspace.id);
      fetchRecycleBin(accessToken, activeWorkspace.id);
      fetchTags(accessToken, activeWorkspace.id);
      fetchTimeline(accessToken, activeWorkspace.id);
    }
  }, [accessToken, activeWorkspace, fetchProjects, fetchFavorites, fetchRecycleBin, fetchTags, fetchTimeline]);

  // Load collections when active project changes
  useEffect(() => {
    if (accessToken && activeProject) {
      fetchCollections(accessToken, activeProject.id);
    }
  }, [accessToken, activeProject, fetchCollections]);

  // Load folders and assets when active collection or folder changes
  useEffect(() => {
    if (accessToken && activeCollection) {
      fetchFolders(accessToken, activeCollection.id, activeFolder?.id);
      fetchAssets(accessToken, activeWorkspace?.id || "", activeFolder?.id);
    }
  }, [accessToken, activeCollection, activeFolder, fetchFolders, fetchAssets, activeWorkspace]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjName || !accessToken || !activeWorkspace) return;
    await createProject(accessToken, activeWorkspace.id, newProjName, newProjDesc);
    setNewProjName("");
    setNewProjDesc("");
  };

  const handleCreateCollection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newColName || !accessToken || !activeProject || !activeWorkspace) return;
    await createCollection(accessToken, activeProject.id, activeWorkspace.id, newColName, newColDesc);
    setNewColName("");
    setNewColDesc("");
  };

  const handleCreateFolder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFolderName || !accessToken || !activeCollection || !activeWorkspace) return;
    await createFolder(
      accessToken, 
      activeCollection.id, 
      activeWorkspace.id, 
      newFolderName, 
      activeFolder?.id
    );
    setNewFolderName("");
  };

  const handleCreateAsset = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAssetName || !accessToken || !activeWorkspace) return;
    await createAsset(
      accessToken,
      activeWorkspace.id,
      newAssetName,
      newAssetType,
      activeFolder?.id,
      { source: "user_upload", extension: newAssetType === "link" ? "" : "txt" }
    );
    setNewAssetName("");
  };

  const handleCreateTag = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTagName || !accessToken || !activeWorkspace) return;
    await createTag(accessToken, activeWorkspace.id, newTagName, "indigo");
    setNewTagName("");
  };

  const handleDeleteAsset = async (assetId: string) => {
    if (!accessToken || !activeWorkspace) return;
    await deleteAsset(accessToken, activeWorkspace.id, assetId);
    if (selectedAsset?.id === assetId) {
      setSelectedAsset(null);
    }
  };

  const handleRestoreItem = async (itemId: string) => {
    if (!accessToken || !activeWorkspace) return;
    await restoreItem(accessToken, activeWorkspace.id, itemId);
  };

  const handlePermanentDelete = async (itemId: string) => {
    if (!accessToken || !activeWorkspace) return;
    await permanentDeleteItem(accessToken, activeWorkspace.id, itemId);
  };

  const handleToggleFav = async (id: string, type: string) => {
    if (!accessToken || !activeWorkspace) return;
    await toggleFavorite(accessToken, activeWorkspace.id, id, type);
  };

  // Filtered Assets list
  const filteredAssets = assets.filter((a) => 
    a.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen text-slate-100 font-sans p-4 md:p-6 text-left flex gap-6">
      
      {/* 1. Left Explorer Navigation Sidebar */}
      <div className="w-64 bg-slate-900 border border-slate-800 rounded-2xl p-4 shrink-0 flex flex-col gap-5 max-h-[calc(100vh-4rem)] overflow-y-auto">
        <div>
          <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2">
            Active Projects
          </span>
          <div className="flex flex-col gap-1">
            {projects.map((p) => (
              <button
                key={p.id}
                onClick={() => { setActiveProject(p); setActiveCollection(null); setActiveFolder(null); setShowRecycleBin(false); }}
                className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                  activeProject?.id === p.id && !showRecycleBin ? "bg-slate-950 text-indigo-400 border border-slate-850" : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <Briefcase className="w-3.5 h-3.5" />
                  <span className="truncate">{p.name}</span>
                </div>
              </button>
            ))}
          </div>

          <form onSubmit={handleCreateProject} className="mt-2 flex gap-1">
            <input
              type="text"
              placeholder="New Project..."
              value={newProjName}
              onChange={(e) => setNewProjName(e.target.value)}
              className="flex-1 px-2 py-1 bg-slate-950 border border-slate-850 rounded text-[10px] text-white placeholder-slate-700 outline-none"
            />
            <button type="submit" className="p-1 bg-indigo-500 rounded hover:bg-indigo-600 text-white">
              <Plus className="w-3 h-3" />
            </button>
          </form>
        </div>

        {activeProject && (
          <div>
            <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2">
              Collections ({activeProject.name})
            </span>
            <div className="flex flex-col gap-1">
              {collections.map((c) => (
                <button
                  key={c.id}
                  onClick={() => { setActiveCollection(c); setActiveFolder(null); setShowRecycleBin(false); }}
                  className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeCollection?.id === c.id && !showRecycleBin ? "bg-slate-950 text-indigo-400 border border-slate-850" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <Layers className="w-3.5 h-3.5" />
                    <span className="truncate">{c.name}</span>
                  </div>
                </button>
              ))}
            </div>

            <form onSubmit={handleCreateCollection} className="mt-2 flex gap-1">
              <input
                type="text"
                placeholder="New Collection..."
                value={newColName}
                onChange={(e) => setNewColName(e.target.value)}
                className="flex-1 px-2 py-1 bg-slate-950 border border-slate-850 rounded text-[10px] text-white placeholder-slate-700 outline-none"
              />
              <button type="submit" className="p-1 bg-indigo-500 rounded hover:bg-indigo-600 text-white">
                <Plus className="w-3 h-3" />
              </button>
            </form>
          </div>
        )}

        <div className="border-t border-slate-850 pt-3 mt-auto">
          <button
            onClick={() => setShowRecycleBin(true)}
            className={`w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-semibold ${
              showRecycleBin ? "bg-slate-950 text-indigo-400 border border-slate-850" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Trash2 className="w-4 h-4 text-slate-500" />
            <span>Recycle Bin</span>
          </button>
        </div>
      </div>

      {/* 2. Middle Main Explorer Feed Panel */}
      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col gap-6 max-h-[calc(100vh-4rem)] overflow-y-auto">
        {showRecycleBin ? (
          /* Recycle Bin View */
          <div className="flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-lg font-bold text-white">Workspace Recycle Bin</h2>
                <p className="text-[10px] text-slate-500 mt-0.5">Restore soft deleted documents and knowledge assets.</p>
              </div>
            </div>
            
            <div className="flex flex-col gap-2">
              {recycleBin.length === 0 ? (
                <div className="text-center py-10 text-slate-600 text-xs font-semibold">
                  Recycle bin is empty.
                </div>
              ) : (
                recycleBin.map((r) => (
                  <div key={r.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-950/80 border border-slate-850 text-xs">
                    <div className="flex items-center gap-3">
                      <FileText className="w-4 h-4 text-slate-500" />
                      <div className="flex flex-col">
                        <span className="font-semibold text-slate-200">Asset UUID: {r.item_id}</span>
                        <span className="text-[9px] text-slate-500 mt-0.5">Trashed on {new Date(r.deleted_at).toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleRestoreItem(r.item_id)}
                        className="px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 text-[10px] font-bold uppercase transition-colors"
                      >
                        Restore
                      </button>
                      <button
                        onClick={() => handlePermanentDelete(r.item_id)}
                        className="p-1.5 text-slate-500 hover:text-rose-400 transition-colors"
                        title="Delete permanently"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        ) : (
          /* Knowledge Explorer View */
          <div className="flex flex-col gap-6">
            
            {/* Explorer Header and Search */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                {activeFolder && (
                  <button
                    onClick={() => setActiveFolder(null)}
                    className="p-1 bg-slate-950 border border-slate-850 rounded hover:text-indigo-400 transition-colors shrink-0"
                  >
                    <ArrowLeft className="w-4 h-4" />
                  </button>
                )}
                <div>
                  <h2 className="text-lg font-bold text-white">
                    {activeFolder ? activeFolder.name : activeCollection ? activeCollection.name : "Documents Explorer"}
                  </h2>
                  <p className="text-[10px] text-slate-500 mt-0.5">
                    {activeFolder ? "Viewing folder files contents" : activeCollection ? "Viewing collection sub-trees" : "Select a project to start"}
                  </p>
                </div>
              </div>

              <div className="relative max-w-xs w-full">
                <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-slate-600" />
                <input
                  type="text"
                  placeholder="Search assets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-850 rounded-lg text-xs text-white placeholder-slate-700 outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>

            {/* Folders creation and listing */}
            {activeCollection && (
              <div className="flex flex-col gap-3">
                <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Folders</span>
                  <form onSubmit={handleCreateFolder} className="flex gap-1.5">
                    <input
                      type="text"
                      placeholder="New folder name..."
                      value={newFolderName}
                      onChange={(e) => setNewFolderName(e.target.value)}
                      className="px-2 py-1 bg-slate-950 border border-slate-850 rounded text-[10px] text-white outline-none"
                    />
                    <button type="submit" className="px-2 py-1 bg-indigo-500 text-white text-[10px] font-semibold rounded hover:bg-indigo-600">
                      Create
                    </button>
                  </form>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {folders.map((f) => (
                    <div
                      key={f.id}
                      onClick={() => setActiveFolder(f)}
                      className="p-3 rounded-xl bg-slate-950/80 border border-slate-850 hover:border-slate-750 transition-all cursor-pointer flex items-center justify-between group"
                    >
                      <div className="flex items-center gap-2.5 truncate">
                        <FolderIcon className="w-4 h-4 text-indigo-400 shrink-0" />
                        <span className="text-xs font-semibold text-slate-200 truncate">{f.name}</span>
                      </div>
                      <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-slate-400 transition-colors" />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Assets creation and listing */}
            {activeCollection && (
              <div className="flex flex-col gap-3">
                <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Assets</span>
                  <form onSubmit={handleCreateAsset} className="flex gap-1.5">
                    <input
                      type="text"
                      placeholder="Asset name..."
                      value={newAssetName}
                      onChange={(e) => setNewAssetName(e.target.value)}
                      className="px-2.5 py-1 bg-slate-950 border border-slate-850 rounded text-[10px] text-white outline-none"
                    />
                    <select
                      value={newAssetType}
                      onChange={(e) => setNewAssetType(e.target.value)}
                      className="px-2 py-1 bg-slate-950 border border-slate-850 rounded text-[10px] text-white outline-none"
                    >
                      <option value="document">Document</option>
                      <option value="link">Web Link</option>
                      <option value="code">Code Script</option>
                    </select>
                    <button type="submit" className="px-2.5 py-1 bg-indigo-500 text-white text-[10px] font-semibold rounded hover:bg-indigo-600">
                      Upload
                    </button>
                  </form>
                </div>

                <div className="flex flex-col gap-2">
                  {filteredAssets.length === 0 ? (
                    <div className="text-center py-10 text-slate-600 text-xs font-semibold">
                      No assets found in this folder.
                    </div>
                  ) : (
                    filteredAssets.map((a) => (
                      <div
                        key={a.id}
                        onClick={() => setSelectedAsset(a)}
                        className={`flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer ${
                          selectedAsset?.id === a.id ? "bg-slate-950 border-indigo-500" : "bg-slate-950/80 border-slate-850 hover:border-slate-800"
                        }`}
                      >
                        <div className="flex items-center gap-3 truncate">
                          {a.asset_type === "link" ? (
                            <LinkIcon className="w-4 h-4 text-emerald-400 shrink-0" />
                          ) : (
                            <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
                          )}
                          <div className="flex flex-col text-left truncate">
                            <span className="text-xs font-semibold text-slate-200 truncate">{a.name}</span>
                            <span className="text-[9px] text-slate-500 mt-0.5 uppercase tracking-wider">{a.asset_type}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <button
                            onClick={(e) => { e.stopPropagation(); handleToggleFav(a.id, "asset"); }}
                            className="p-1.5 text-slate-500 hover:text-amber-400 transition-colors"
                          >
                            <Star className={`w-3.5 h-3.5 ${favorites.some((f) => f.target_id === a.id) ? "fill-amber-400 text-amber-400" : ""}`} />
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleDeleteAsset(a.id); }}
                            className="p-1.5 text-slate-500 hover:text-rose-400 transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 3. Right Metadata Settings Panel */}
      <div className="w-80 bg-slate-900 border border-slate-800 rounded-2xl p-5 shrink-0 flex flex-col gap-6 max-h-[calc(100vh-4rem)] overflow-y-auto">
        {selectedAsset ? (
          <div className="flex flex-col gap-5">
            <div className="flex items-center gap-2 border-b border-slate-850 pb-3">
              <Info className="w-4 h-4 text-indigo-400 shrink-0" />
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Metadata Details</span>
            </div>

            <div className="flex flex-col gap-3.5 text-xs text-left">
              <div className="flex flex-col gap-0.5">
                <span className="text-[10px] font-bold text-slate-500 uppercase">Asset Name</span>
                <span className="font-semibold text-slate-200 break-all">{selectedAsset.name}</span>
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="text-[10px] font-bold text-slate-500 uppercase">Asset Classification</span>
                <span className="font-mono text-slate-400 uppercase">{selectedAsset.asset_type}</span>
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="text-[10px] font-bold text-slate-500 uppercase">Creation Date</span>
                <span className="text-slate-400">{new Date(selectedAsset.created_at).toLocaleString()}</span>
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="text-[10px] font-bold text-slate-500 uppercase">Unique ID</span>
                <span className="font-mono text-slate-500 text-[10px]">{selectedAsset.id}</span>
              </div>
            </div>

            {/* Tags section */}
            <div className="border-t border-slate-850 pt-4 flex flex-col gap-3">
              <span className="text-[10px] font-bold text-slate-500 uppercase">Asset Index Tags</span>
              
              <div className="flex flex-wrap gap-1.5">
                {tags.map((t) => (
                  <span key={t.id} className="px-2 py-0.5 bg-slate-950 border border-slate-850 rounded-full text-[10px] font-semibold text-slate-400 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                    {t.name}
                  </span>
                ))}
              </div>

              <form onSubmit={handleCreateTag} className="flex gap-1.5">
                <input
                  type="text"
                  placeholder="Add custom tag..."
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  className="flex-1 px-2.5 py-1.5 bg-slate-950 border border-slate-850 rounded text-[10px] text-white outline-none"
                />
                <button type="submit" className="px-2 py-1.5 bg-indigo-500 text-white text-[10px] font-semibold rounded hover:bg-indigo-600">
                  Add
                </button>
              </form>
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-600">
            <Info className="w-8 h-8 text-slate-700 mb-2" />
            <p className="text-xs font-semibold">Select a document or link asset to view its metadata properties.</p>
          </div>
        )}
      </div>

    </div>
  );
};
export default Documents;
