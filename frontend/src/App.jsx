import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8001";

const artifacts = [
  {
    name: "Project Charter",
    path: "project-charter",
    description: "Project objectives, scope and governance",
  },
  {
    name: "WBS",
    path: "wbs",
    description: "Work breakdown structure and effort",
  },
  {
    name: "Requirements Register",
    path: "requirements-register",
    description: "Business and functional requirements",
  },
  {
    name: "RAID & Risk Register",
    path: "raid-risk-register",
    description: "Risks, assumptions, issues and dependencies",
  },
  {
    name: "Stakeholder Register",
    path: "stakeholder-register",
    description: "Stakeholder engagement and communication",
  },
  {
    name: "RACI Matrix",
    path: "raci-matrix",
    description: "Responsibility and accountability matrix",
  },
  {
    name: "Project Timeline",
    path: "project-timeline",
    description: "Milestones, dependencies and project schedule",
  },
];

function App() {
  // Authentication
  const [token, setToken] = useState(
    () => localStorage.getItem("pmo_ai_token") || ""
  );
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState("");

  const handleLogout = () => {
    localStorage.removeItem("pmo_ai_token");
    setToken("");
    setProjects([]);
    setSelectedProject(null);
    setSelectedDocument(null);
    setDocuments([]);
    setError("");
  };

  const authFetch = async (url, options = {}) => {
    const headers = new Headers(options.headers || {});

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401 && token) {
      localStorage.removeItem("pmo_ai_token");
      setToken("");
    }

    return response;
  };

  const handleLogin = async (event) => {
    event.preventDefault();

    if (!loginEmail.trim() || !loginPassword) {
      setLoginError("Email and password are required.");
      return;
    }

    setLoginLoading(true);
    setLoginError("");

    try {
      const body = new URLSearchParams();
      body.append("username", loginEmail.trim());
      body.append("password", loginPassword);

      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail || "Invalid email or password"
        );
      }

      const data = await response.json();

      localStorage.setItem(
        "pmo_ai_token",
        data.access_token
      );

      setToken(data.access_token);
      setLoginPassword("");
    } catch (err) {
      setLoginError(err.message);
    } finally {
      setLoginLoading(false);
    }
  };

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Create project
  const [showForm, setShowForm] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [creating, setCreating] = useState(false);

  // Edit / delete project
  const [editingProject, setEditingProject] = useState(null);
  const [editProjectName, setEditProjectName] = useState("");
  const [editProjectDescription, setEditProjectDescription] =
    useState("");
  const [editProjectStatus, setEditProjectStatus] =
    useState("Draft");
  const [savingProject, setSavingProject] = useState(false);
  const [deletingProjectId, setDeletingProjectId] =
    useState(null);

  // Selected project / documents
  const [selectedProject, setSelectedProject] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [deletingDocumentId, setDeletingDocumentId] = useState(null);

  // Upload
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadKey, setUploadKey] = useState(0);

  // BRD analysis
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisMessage, setAnalysisMessage] = useState("");
  const [analysisStatus, setAnalysisStatus] =
    useState("unknown");

  // PMO artifacts
  const [artifactLoading, setArtifactLoading] = useState("");
  const [artifactMessage, setArtifactMessage] = useState("");
  const [artifactStatuses, setArtifactStatuses] = useState({});

  // --------------------------------------------------
  // LOAD PROJECTS
  // --------------------------------------------------

  const loadProjects = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await authFetch(`${API_URL}/projects`);

      if (!response.ok) {
        throw new Error("Failed to load projects");
      }

      const data = await response.json();
      setProjects(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadProjects();
    } else {
      setLoading(false);
      setProjects([]);
    }
  }, [token]);

  // --------------------------------------------------
  // ANALYSIS STATUS
  // --------------------------------------------------

  const loadAnalysisStatus = async (documentId) => {
    setAnalysisStatus("checking");

    try {
      const response = await authFetch(
        `${API_URL}/documents/${documentId}/analysis`
      );

      if (response.ok) {
        setAnalysisStatus("cached");
        return;
      }

      if (response.status === 404) {
        setAnalysisStatus("not-analyzed");
        return;
      }

      setAnalysisStatus("error");
    } catch {
      setAnalysisStatus("error");
    }
  };

  // --------------------------------------------------
  // ARTIFACT STATUS
  // --------------------------------------------------

  const loadArtifactStatuses = async (documentId) => {
    const initialStatuses = {};

    artifacts.forEach((artifact) => {
      initialStatuses[artifact.path] = "checking";
    });

    setArtifactStatuses(initialStatuses);

    const results = await Promise.all(
      artifacts.map(async (artifact) => {
        try {
          const response = await authFetch(
            `${API_URL}/documents/${documentId}/artifacts/${artifact.path}`
          );

          if (response.ok) {
            return {
              path: artifact.path,
              status: "cached",
            };
          }

          if (response.status === 404) {
            return {
              path: artifact.path,
              status: "not-generated",
            };
          }

          return {
            path: artifact.path,
            status: "error",
          };
        } catch {
          return {
            path: artifact.path,
            status: "error",
          };
        }
      })
    );

    const updatedStatuses = {};

    results.forEach((result) => {
      updatedStatuses[result.path] = result.status;
    });

    setArtifactStatuses(updatedStatuses);
  };

  // --------------------------------------------------
  // CREATE PROJECT
  // --------------------------------------------------

  const handleCreateProject = async (event) => {
    event.preventDefault();

    if (!projectName.trim()) {
      setError("Project name is required.");
      return;
    }

    setCreating(true);
    setError("");

    try {
      const response = await authFetch(`${API_URL}/projects`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: projectName.trim(),
          description: projectDescription.trim() || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || "Failed to create project"
        );
      }

      const newProject = await response.json();

      setProjects((currentProjects) => [
        ...currentProjects,
        newProject,
      ]);

      setProjectName("");
      setProjectDescription("");
      setShowForm(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  // --------------------------------------------------
  // EDIT PROJECT
  // --------------------------------------------------

  const handleStartEditProject = (project) => {
    setEditingProject(project);

    setEditProjectName(project.name || "");

    setEditProjectDescription(
      project.description || ""
    );

    setEditProjectStatus(
      project.status || "Draft"
    );

    setShowForm(false);
    setError("");
  };

  const handleCancelEditProject = () => {
    setEditingProject(null);
    setEditProjectName("");
    setEditProjectDescription("");
    setEditProjectStatus("Draft");
    setError("");
  };

  const handleUpdateProject = async (event) => {
    event.preventDefault();

    if (!editingProject) {
      return;
    }

    if (!editProjectName.trim()) {
      setError("Project name is required.");
      return;
    }

    setSavingProject(true);
    setError("");

    try {
      const response = await authFetch(
        `${API_URL}/projects/${editingProject.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: editProjectName.trim(),
            description:
              editProjectDescription.trim() || null,
            status: editProjectStatus,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => null);

        throw new Error(
          errorData?.detail ||
            "Failed to update project"
        );
      }

      const updatedProject =
        await response.json();

      setProjects((currentProjects) =>
        currentProjects.map((project) =>
          project.id === updatedProject.id
            ? updatedProject
            : project
        )
      );

      if (
        selectedProject &&
        selectedProject.id === updatedProject.id
      ) {
        setSelectedProject(updatedProject);
      }

      setEditingProject(null);
      setEditProjectName("");
      setEditProjectDescription("");
      setEditProjectStatus("Draft");
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingProject(false);
    }
  };

  // --------------------------------------------------
  // DELETE PROJECT
  // --------------------------------------------------

  const handleDeleteProject = async (project) => {
    const confirmed = window.confirm(
      `Delete project "${project.name}"?\n\n` +
        "This action is permanent and may remove related project data.\n\n" +
        "Do you want to continue?"
    );

    if (!confirmed) {
      return;
    }

    setDeletingProjectId(project.id);
    setError("");

    try {
      const response = await authFetch(
        `${API_URL}/projects/${project.id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => null);

        throw new Error(
          errorData?.detail ||
            "Failed to delete project"
        );
      }

      setProjects((currentProjects) =>
        currentProjects.filter(
          (currentProject) =>
            currentProject.id !== project.id
        )
      );

      if (
        editingProject &&
        editingProject.id === project.id
      ) {
        handleCancelEditProject();
      }

      if (
        selectedProject &&
        selectedProject.id === project.id
      ) {
        handleBackToDashboard();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingProjectId(null);
    }
  };

  // --------------------------------------------------
  // OPEN PROJECT
  // --------------------------------------------------

  const handleOpenProject = async (project) => {
    setSelectedProject(project);
    setSelectedDocument(null);
    setDocuments([]);
    setDocumentsLoading(true);

    setError("");
    setUploadMessage("");
    setAnalysisMessage("");
    setArtifactMessage("");

    setAnalysisStatus("unknown");
    setArtifactStatuses({});

    try {
      const response = await authFetch(
        `${API_URL}/projects/${project.id}/documents`
      );

      if (!response.ok) {
        throw new Error(
          "Failed to load project documents"
        );
      }

      const data = await response.json();
      setDocuments(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setDocumentsLoading(false);
    }
  };

  // --------------------------------------------------
  // OPEN DOCUMENT
  // --------------------------------------------------

  const handleOpenDocument = async (document) => {
    setSelectedDocument(document);

    setAnalysisMessage("");
    setArtifactMessage("");
    setError("");

    await Promise.all([
      loadAnalysisStatus(document.id),
      loadArtifactStatuses(document.id),
    ]);
  };

  // --------------------------------------------------
  // DELETE DOCUMENT
  // --------------------------------------------------

  const handleDeleteDocument = async (document) => {
    const confirmed = window.confirm(
      `Delete document "${document.original_name}"?\n\n` +
        "This action is permanent and may also remove its analysis and generated artifacts.\n\n" +
        "Do you want to continue?"
    );

    if (!confirmed) {
      return;
    }

    setDeletingDocumentId(document.id);
    setError("");
    setUploadMessage("");
    setAnalysisMessage("");
    setArtifactMessage("");

    try {
      const response = await authFetch(
        `${API_URL}/documents/${document.id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => null);

        throw new Error(
          errorData?.detail ||
            "Failed to delete document"
        );
      }

      setDocuments((currentDocuments) =>
        currentDocuments.filter(
          (currentDocument) =>
            currentDocument.id !== document.id
        )
      );

      if (
        selectedDocument &&
        selectedDocument.id === document.id
      ) {
        setSelectedDocument(null);
        setAnalysisStatus("unknown");
        setArtifactStatuses({});
        setAnalysisMessage("");
        setArtifactMessage("");
      }

      setUploadMessage(
        `${document.original_name} deleted successfully.`
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingDocumentId(null);
    }
  };

  // --------------------------------------------------
  // UPLOAD DOCUMENT
  // --------------------------------------------------

  const handleUploadDocument = async (event) => {
    event.preventDefault();

    if (!selectedProject) {
      setError("Please open a project first.");
      return;
    }

    if (!uploadFile) {
      setError(
        "Please select a PDF or DOCX file."
      );
      return;
    }

    const allowedExtensions = [
      ".pdf",
      ".docx",
    ];

    const fileName =
      uploadFile.name.toLowerCase();

    const isAllowed =
      allowedExtensions.some((extension) =>
        fileName.endsWith(extension)
      );

    if (!isAllowed) {
      setError(
        "Only PDF and DOCX files are allowed."
      );
      return;
    }

    const maxSize =
      10 * 1024 * 1024;

    if (uploadFile.size > maxSize) {
      setError(
        "File size cannot exceed 10 MB."
      );
      return;
    }

    setUploading(true);
    setError("");
    setUploadMessage("");

    try {
      const formData = new FormData();

      formData.append(
        "file",
        uploadFile
      );

      const response = await authFetch(
        `${API_URL}/projects/${selectedProject.id}/documents`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData =
          await response
            .json()
            .catch(() => null);

        throw new Error(
          errorData?.detail ||
            "Failed to upload document"
        );
      }

      const newDocument =
        await response.json();

      setDocuments((currentDocuments) => [
        newDocument,
        ...currentDocuments,
      ]);

      setUploadFile(null);

      setUploadKey(
        (currentKey) =>
          currentKey + 1
      );

      setUploadMessage(
        `${newDocument.original_name} uploaded successfully.`
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  // --------------------------------------------------
  // ANALYZE BRD
  // --------------------------------------------------

  const handleAnalyzeDocument = async () => {
    if (!selectedDocument) {
      setError(
        "Please open a document first."
      );
      return;
    }

    setAnalyzing(true);
    setError("");
    setAnalysisMessage("");

    try {
      const cachedResponse =
        await authFetch(
          `${API_URL}/documents/${selectedDocument.id}/analysis`
        );

      if (cachedResponse.ok) {
        setAnalysisStatus("cached");

        setAnalysisMessage(
          "Cached BRD analysis loaded successfully."
        );

        return;
      }

      if (
        cachedResponse.status !== 404
      ) {
        const errorData =
          await cachedResponse
            .json()
            .catch(() => null);

        throw new Error(
          errorData?.detail ||
            "Unable to check existing BRD analysis"
        );
      }

      setAnalysisStatus(
        "not-analyzed"
      );

      const confirmed =
        window.confirm(
          "No cached BRD analysis exists for this document.\n\n" +
            "Analyzing this BRD will call the OpenAI API and may incur a small cost.\n\n" +
            "Do you want to continue?"
        );

      if (!confirmed) {
        setAnalysisMessage(
          "BRD analysis cancelled."
        );
        return;
      }

      const response =
        await authFetch(
          `${API_URL}/documents/${selectedDocument.id}/analyze?force=false`,
          {
            method: "POST",
          }
        );

      if (!response.ok) {
        const errorData =
          await response
            .json()
            .catch(() => null);

        throw new Error(
          errorData?.detail ||
            "Failed to analyze document"
        );
      }

      const data =
        await response.json();

      setAnalysisStatus("cached");

      setAnalysisMessage(
        data.cached
          ? "Cached BRD analysis loaded successfully."
          : "BRD analysis completed successfully."
      );
    } catch (err) {
      setAnalysisStatus("error");
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  // --------------------------------------------------
  // GENERATE / LOAD ARTIFACT
  // --------------------------------------------------

  const handleGenerateArtifact = async (
    artifactPath,
    artifactName
  ) => {
    if (!selectedDocument) {
      setError(
        "Please open a document first."
      );
      return;
    }

    if (
      analysisStatus !== "cached"
    ) {
      setError(
        "Please analyze the BRD before generating PMO artifacts."
      );
      return;
    }

    setArtifactLoading(
      artifactPath
    );

    setArtifactMessage("");
    setError("");

    try {
      const cachedResponse =
        await authFetch(
          `${API_URL}/documents/${selectedDocument.id}/artifacts/${artifactPath}`
        );

      if (cachedResponse.ok) {
        setArtifactStatuses(
          (current) => ({
            ...current,
            [artifactPath]:
              "cached",
          })
        );

        setArtifactMessage(
          `${artifactName} loaded from cache successfully.`
        );

        return;
      }

      if (
        cachedResponse.status !==
        404
      ) {
        const errorData =
          await cachedResponse
            .json()
            .catch(() => null);

        throw new Error(
          errorData?.detail ||
            `Unable to check existing ${artifactName}`
        );
      }

      setArtifactStatuses(
        (current) => ({
          ...current,
          [artifactPath]:
            "not-generated",
        })
      );

      const confirmed =
        window.confirm(
          `${artifactName} is not cached for this document.\n\n` +
            "Generating it will call the OpenAI API and may incur a small cost.\n\n" +
            "Do you want to continue?"
        );

      if (!confirmed) {
        setArtifactMessage(
          `${artifactName} generation cancelled.`
        );
        return;
      }

      const response =
        await authFetch(
          `${API_URL}/documents/${selectedDocument.id}/artifacts/${artifactPath}?force=false`,
          {
            method: "POST",
          }
        );

      if (!response.ok) {
        const errorData =
          await response
            .json()
            .catch(() => null);

        throw new Error(
          errorData?.detail ||
            `Failed to generate ${artifactName}`
        );
      }

      const data =
        await response.json();

      setArtifactStatuses(
        (current) => ({
          ...current,
          [artifactPath]:
            "cached",
        })
      );

      setArtifactMessage(
        data.cached
          ? `${artifactName} loaded from cache successfully.`
          : `${artifactName} generated successfully.`
      );
    } catch (err) {
      setArtifactStatuses(
        (current) => ({
          ...current,
          [artifactPath]:
            "error",
        })
      );

      setError(err.message);
    } finally {
      setArtifactLoading("");
    }
  };

  // --------------------------------------------------
  // BACK TO DASHBOARD
  // --------------------------------------------------

  const handleBackToDashboard = () => {
    setSelectedProject(null);
    setSelectedDocument(null);

    setDocuments([]);
    setUploadFile(null);

    setUploadMessage("");
    setAnalysisMessage("");
    setArtifactMessage("");

    setAnalysisStatus("unknown");
    setArtifactStatuses({});

    setError("");
  };

  // --------------------------------------------------
  // DOWNLOAD
  // --------------------------------------------------

  const downloadAuthenticatedFile = async (
    url,
    fallbackFilename
  ) => {
    try {
      setError("");

      const response = await authFetch(url);

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => null);

        throw new Error(
          errorData?.detail || "Download failed"
        );
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);

      const contentDisposition =
        response.headers.get("content-disposition") || "";

      const filenameMatch = contentDisposition.match(
        /filename="?([^"]+)"?/i
      );

      const filename =
        filenameMatch?.[1] || fallbackFilename;

      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();

      URL.revokeObjectURL(objectUrl);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDownloadDocument = (
    documentId
  ) => {
    downloadAuthenticatedFile(
      `${API_URL}/documents/${documentId}/download`,
      `document_${documentId}`
    );
  };

  const handleDownloadArtifact = (
    documentId,
    artifactPath
  ) => {
    downloadAuthenticatedFile(
      `${API_URL}/documents/${documentId}/artifacts/${artifactPath}/download`,
      `${artifactPath}_${documentId}`
    );
  };

  // --------------------------------------------------
  // STATUS LABEL HELPERS
  // --------------------------------------------------

  const getArtifactStatusLabel = (
    artifactPath
  ) => {
    const status =
      artifactStatuses[
        artifactPath
      ];

    if (
      status === "checking"
    ) {
      return "Checking...";
    }

    if (
      status === "cached"
    ) {
      return "Cached";
    }

    if (
      status ===
      "not-generated"
    ) {
      return "Not Generated";
    }

    if (
      status === "error"
    ) {
      return "Status Error";
    }

    return "Unknown";
  };

  const getArtifactStatusClass = (
    artifactPath
  ) => {
    const status =
      artifactStatuses[
        artifactPath
      ];

    if (
      status === "cached"
    ) {
      return "artifact-status cached";
    }

    if (
      status ===
      "not-generated"
    ) {
      return "artifact-status not-generated";
    }

    if (
      status === "error"
    ) {
      return "artifact-status status-error";
    }

    return "artifact-status checking";
  };

  const getAnalysisStatusLabel =
    () => {
      if (
        analysisStatus ===
        "checking"
      ) {
        return "Checking Analysis...";
      }

      if (
        analysisStatus ===
        "cached"
      ) {
        return "BRD Analysis: Cached";
      }

      if (
        analysisStatus ===
        "not-analyzed"
      ) {
        return "BRD Analysis: Not Analyzed";
      }

      if (
        analysisStatus ===
        "error"
      ) {
        return "BRD Analysis: Status Error";
      }

      return "BRD Analysis: Unknown";
    };

  const totalProjects =
    projects.length;

  // ==================================================
  // LOGIN
  // ==================================================

  if (!token) {
    return (
      <div className="login-page">
        <section className="login-card">
          <div className="login-brand">
            <h1>PMO AI Assistant</h1>
            <p>
              Sign in to your AI-powered project management workspace.
            </p>
          </div>

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="loginEmail">
                Email
              </label>

              <input
                id="loginEmail"
                type="email"
                value={loginEmail}
                onChange={(event) =>
                  setLoginEmail(event.target.value)
                }
                placeholder="Enter your email"
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="loginPassword">
                Password
              </label>

              <input
                id="loginPassword"
                type="password"
                value={loginPassword}
                onChange={(event) =>
                  setLoginPassword(event.target.value)
                }
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </div>

            {loginError && (
              <div className="error-message">
                {loginError}
              </div>
            )}

            <button
              type="submit"
              className="primary-button"
              disabled={loginLoading}
            >
              {loginLoading
                ? "Signing in..."
                : "Sign In"}
            </button>
          </form>
        </section>
      </div>
    );
  }


  // ==================================================
  // PROJECT WORKSPACE
  // ==================================================

  if (selectedProject) {
    return (
      <div className="app">
        <aside className="sidebar">
          <div className="brand">
            <h2>PMO AI</h2>
            <span>
              Assistant
            </span>
          </div>

          <nav>
            <a
              href="#"
              onClick={(
                event
              ) => {
                event.preventDefault();

                handleBackToDashboard();
              }}
            >
              Dashboard
            </a>

            <a
              className="active"
              href="#"
              onClick={(
                event
              ) =>
                event.preventDefault()
              }
            >
              Project Workspace
            </a>

            <a
              href="#"
              onClick={(
                event
              ) =>
                event.preventDefault()
              }
            >
              Documents
            </a>

            <a
              href="#"
              onClick={(
                event
              ) =>
                event.preventDefault()
              }
            >
              AI Artifacts
            </a>

            <a
              href="#"
              onClick={(
                event
              ) =>
                event.preventDefault()
              }
            >
              Reports
            </a>
          </nav>
        </aside>

        <main className="main-content">
          <header className="topbar">
            <div>
              <button
                type="button"
                className="back-button"
                onClick={
                  handleBackToDashboard
                }
              >
                ← Back to Dashboard
              </button>

              <h1>
                {
                  selectedProject.name
                }
              </h1>

              <p>
                {selectedProject.description ||
                  "No project description available."}
              </p>
            </div>

            <div className="form-actions">
              <span className="badge">
                {selectedProject.status ||
                  "Draft"}
              </span>

              <button
                type="button"
                className="secondary-button"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          </header>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <section className="workspace">
            <div className="section-header">
              <div>
                <h2>
                  Project Documents
                </h2>

                <p>
                  Select a BRD or project document to access its PMO artifacts.
                </p>
              </div>
            </div>

            <form
              className="upload-panel"
              onSubmit={
                handleUploadDocument
              }
            >
              <div>
                <h3>
                  Upload BRD / Project Document
                </h3>

                <p>
                  Supported formats: PDF and DOCX. Maximum size: 10 MB.
                </p>
              </div>

              <div className="upload-controls">
                <input
                  key={
                    uploadKey
                  }
                  type="file"
                  accept=".pdf,.docx"
                  onChange={(
                    event
                  ) => {
                    setUploadFile(
                      event
                        .target
                        .files?.[0] ||
                        null
                    );

                    setUploadMessage(
                      ""
                    );

                    setError(
                      ""
                    );
                  }}
                />

                <button
                  type="submit"
                  className="primary-button"
                  disabled={
                    uploading
                  }
                >
                  {uploading
                    ? "Uploading..."
                    : "Upload Document"}
                </button>
              </div>

              {uploadFile && (
                <p className="selected-file">
                  Selected:{" "}
                  {
                    uploadFile.name
                  }
                </p>
              )}

              {uploadMessage && (
                <p className="success-message">
                  {
                    uploadMessage
                  }
                </p>
              )}
            </form>

            {documentsLoading && (
              <p>
                Loading documents...
              </p>
            )}

            {!documentsLoading &&
              documents.length ===
                0 && (
                <div className="empty-state">
                  <h3>
                    No documents found
                  </h3>

                  <p>
                    Upload a BRD to begin AI analysis and artifact generation.
                  </p>
                </div>
              )}

            <div className="documents-grid">
              {documents.map(
                (document) => (
                  <div
                    className={`document-card ${
                      selectedDocument?.id ===
                      document.id
                        ? "selected-document"
                        : ""
                    }`}
                    key={
                      document.id
                    }
                  >
                    <div className="document-type">
                      {document.file_type?.toUpperCase() ||
                        "FILE"}
                    </div>

                    <h3>
                      {
                        document.original_name
                      }
                    </h3>

                    <p>
                      Document ID:{" "}
                      {
                        document.id
                      }
                    </p>

                    <p>
                      Size:{" "}
                      {document.file_size
                        ? (
                            document.file_size /
                            1024
                          ).toFixed(
                            1
                          )
                        : "0.0"}{" "}
                      KB
                    </p>

                    <div className="document-actions">
                      <button
                        type="button"
                        className="primary-button"
                        onClick={() =>
                          handleOpenDocument(
                            document
                          )
                        }
                      >
                        Open Document
                      </button>

                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() =>
                          handleDownloadDocument(
                            document.id
                          )
                        }
                      >
                        Download
                      </button>

                      <button
                        type="button"
                        className="secondary-button"
                        disabled={
                          deletingDocumentId ===
                          document.id
                        }
                        onClick={() =>
                          handleDeleteDocument(
                            document
                          )
                        }
                      >
                        {deletingDocumentId ===
                        document.id
                          ? "Deleting..."
                          : "Delete"}
                      </button>
                    </div>
                  </div>
                )
              )}
            </div>
          </section>

          {selectedDocument && (
            <section className="workspace artifact-workspace">
              <div className="section-header">
                <div>
                  <h2>
                    PMO AI Artifacts
                  </h2>

                  <p>
                    Document:{" "}
                    <strong>
                      {
                        selectedDocument.original_name
                      }
                    </strong>
                  </p>

                  <p>
                    Document ID:{" "}
                    {
                      selectedDocument.id
                    }
                  </p>

                  <div
                    className={`analysis-status ${analysisStatus}`}
                  >
                    {
                      getAnalysisStatusLabel()
                    }
                  </div>

                  <div className="analysis-actions">
                    <button
                      type="button"
                      className="primary-button"
                      onClick={
                        handleAnalyzeDocument
                      }
                      disabled={
                        analyzing ||
                        analysisStatus ===
                          "checking"
                      }
                    >
                      {analyzing
                        ? "Analyzing BRD..."
                        : analysisStatus ===
                            "cached"
                          ? "Load Cached Analysis"
                          : "Analyze BRD"}
                    </button>

                    {analysisMessage && (
                      <span className="analysis-success">
                        {
                          analysisMessage
                        }
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="artifact-grid">
                {artifacts.map(
                  (
                    artifact,
                    index
                  ) => (
                    <div
                      className="artifact-card"
                      key={
                        artifact.path
                      }
                    >
                      <span>
                        {String(
                          index +
                            1
                        ).padStart(
                          2,
                          "0"
                        )}
                      </span>

                      <div
                        className={getArtifactStatusClass(
                          artifact.path
                        )}
                      >
                        {getArtifactStatusLabel(
                          artifact.path
                        )}
                      </div>

                      <h3>
                        {
                          artifact.name
                        }
                      </h3>

                      <p>
                        {
                          artifact.description
                        }
                      </p>

                      <div className="artifact-actions">
                        <button
                          type="button"
                          className="primary-button"
                          onClick={() =>
                            handleGenerateArtifact(
                              artifact.path,
                              artifact.name
                            )
                          }
                          disabled={
                            artifactLoading ===
                              artifact.path ||
                            artifactStatuses[
                              artifact
                                .path
                            ] ===
                              "checking" ||
                            analysisStatus !==
                              "cached"
                          }
                        >
                          {artifactLoading ===
                          artifact.path
                            ? "Loading..."
                            : artifactStatuses[
                                  artifact
                                    .path
                                ] ===
                                "cached"
                              ? "Load Cached"
                              : "Generate"}
                        </button>

                        <button
                          type="button"
                          className="artifact-download-button"
                          onClick={() =>
                            handleDownloadArtifact(
                              selectedDocument.id,
                              artifact.path
                            )
                          }
                          disabled={
                            artifactStatuses[
                              artifact
                                .path
                            ] !==
                            "cached"
                          }
                        >
                          Download Artifact
                        </button>
                      </div>
                    </div>
                  )
                )}
              </div>

              {artifactMessage && (
                <p className="analysis-success">
                  {
                    artifactMessage
                  }
                </p>
              )}
            </section>
          )}
        </main>
      </div>
    );
  }

  // ==================================================
  // DASHBOARD
  // ==================================================

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <h2>
            PMO AI
          </h2>

          <span>
            Assistant
          </span>
        </div>

        <nav>
          <a
            className="active"
            href="#"
            onClick={(
              event
            ) =>
              event.preventDefault()
            }
          >
            Dashboard
          </a>

          <a
            href="#"
            onClick={(
              event
            ) =>
              event.preventDefault()
            }
          >
            Projects
          </a>

          <a
            href="#"
            onClick={(
              event
            ) =>
              event.preventDefault()
            }
          >
            Documents
          </a>

          <a
            href="#"
            onClick={(
              event
            ) =>
              event.preventDefault()
            }
          >
            AI Artifacts
          </a>

          <a
            href="#"
            onClick={(
              event
            ) =>
              event.preventDefault()
            }
          >
            Reports
          </a>

          <a
            href="#"
            onClick={(
              event
            ) =>
              event.preventDefault()
            }
          >
            Settings
          </a>
        </nav>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>
              PMO AI Assistant
            </h1>

            <p>
              AI-powered project management workspace
            </p>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="primary-button"
              onClick={() => {
                setShowForm(
                  true
                );

                setEditingProject(
                  null
                );

                setError(
                  ""
                );
              }}
            >
              + New Project
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        </header>

        <section className="stats-grid">
          <div className="stat-card">
            <span>
              Total Projects
            </span>

            <strong>
              {loading
                ? "..."
                : totalProjects}
            </strong>

            <p>
              Projects from PostgreSQL
            </p>
          </div>

          <div className="stat-card">
            <span>
              Backend
            </span>

            <strong className="status">
              {error
                ? "Check"
                : "Healthy"}
            </strong>

            <p>
              FastAPI service
            </p>
          </div>

          <div className="stat-card">
            <span>
              PMO Artifacts
            </span>

            <strong>
              7
            </strong>

            <p>
              Supported artifact types
            </p>
          </div>

          <div className="stat-card">
            <span>
              Platform
            </span>

            <strong className="status">
              Active
            </strong>

            <p>
              PMO AI workspace
            </p>
          </div>
        </section>

        {/* CREATE PROJECT FORM */}

        {showForm && (
          <section className="create-project-panel">
            <div className="form-header">
              <div>
                <h2>
                  Create New Project
                </h2>

                <p>
                  Add a project to the workspace.
                </p>
              </div>

              <button
                type="button"
                className="close-button"
                onClick={() => {
                  setShowForm(
                    false
                  );

                  setError(
                    ""
                  );
                }}
              >
                ×
              </button>
            </div>

            <form
              onSubmit={
                handleCreateProject
              }
            >
              <div className="form-group">
                <label htmlFor="projectName">
                  Project Name
                </label>

                <input
                  id="projectName"
                  type="text"
                  value={
                    projectName
                  }
                  onChange={(
                    event
                  ) =>
                    setProjectName(
                      event.target
                        .value
                    )
                  }
                  placeholder="Enter project name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="projectDescription">
                  Description
                </label>

                <textarea
                  id="projectDescription"
                  value={
                    projectDescription
                  }
                  onChange={(
                    event
                  ) =>
                    setProjectDescription(
                      event.target
                        .value
                    )
                  }
                  placeholder="Enter project description"
                  rows="4"
                />
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => {
                    setShowForm(
                      false
                    );

                    setError(
                      ""
                    );
                  }}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={
                    creating
                  }
                >
                  {creating
                    ? "Creating..."
                    : "Create Project"}
                </button>
              </div>
            </form>
          </section>
        )}

        {/* EDIT PROJECT FORM */}

        {editingProject && (
          <section className="create-project-panel">
            <div className="form-header">
              <div>
                <h2>
                  Edit Project
                </h2>

                <p>
                  Update project name, description and status.
                </p>
              </div>

              <button
                type="button"
                className="close-button"
                onClick={
                  handleCancelEditProject
                }
              >
                ×
              </button>
            </div>

            <form
              onSubmit={
                handleUpdateProject
              }
            >
              <div className="form-group">
                <label htmlFor="editProjectName">
                  Project Name
                </label>

                <input
                  id="editProjectName"
                  type="text"
                  value={
                    editProjectName
                  }
                  onChange={(
                    event
                  ) =>
                    setEditProjectName(
                      event.target
                        .value
                    )
                  }
                  placeholder="Enter project name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="editProjectDescription">
                  Description
                </label>

                <textarea
                  id="editProjectDescription"
                  value={
                    editProjectDescription
                  }
                  onChange={(
                    event
                  ) =>
                    setEditProjectDescription(
                      event.target
                        .value
                    )
                  }
                  placeholder="Enter project description"
                  rows="4"
                />
              </div>

              <div className="form-group">
                <label htmlFor="editProjectStatus">
                  Status
                </label>

                <select
                  id="editProjectStatus"
                  value={
                    editProjectStatus
                  }
                  onChange={(
                    event
                  ) =>
                    setEditProjectStatus(
                      event.target
                        .value
                    )
                  }
                >
                  <option value="Draft">
                    Draft
                  </option>

                  <option value="In Progress">
                    In Progress
                  </option>

                  <option value="On Hold">
                    On Hold
                  </option>

                  <option value="Completed">
                    Completed
                  </option>

                  <option value="Cancelled">
                    Cancelled
                  </option>
                </select>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={
                    handleCancelEditProject
                  }
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={
                    savingProject
                  }
                >
                  {savingProject
                    ? "Saving..."
                    : "Save Changes"}
                </button>
              </div>
            </form>
          </section>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <section className="workspace">
          <div className="section-header">
            <div>
              <h2>
                Project Workspace
              </h2>

              <p>
                Projects loaded directly from PostgreSQL.
              </p>
            </div>
          </div>

          {loading && (
            <p>
              Loading projects...
            </p>
          )}

          {!loading &&
            projects.length ===
              0 && (
              <div className="empty-state">
                <h3>
                  No projects found
                </h3>

                <p>
                  Create a project to begin using PMO AI.
                </p>
              </div>
            )}

          {!loading &&
            projects.map(
              (project) => (
                <div
                  className="project-card"
                  key={
                    project.id
                  }
                >
                  <div className="project-header">
                    <div>
                      <span className="badge">
                        {project.status ||
                          "Draft"}
                      </span>

                      <h3>
                        {
                          project.name
                        }
                      </h3>

                      <p>
                        {project.description ||
                          "No project description available."}
                      </p>
                    </div>

                    <div className="form-actions">
                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() =>
                          handleOpenProject(
                            project
                          )
                        }
                      >
                        Open Project
                      </button>

                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() =>
                          handleStartEditProject(
                            project
                          )
                        }
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="secondary-button"
                        disabled={
                          deletingProjectId ===
                          project.id
                        }
                        onClick={() =>
                          handleDeleteProject(
                            project
                          )
                        }
                      >
                        {deletingProjectId ===
                        project.id
                          ? "Deleting..."
                          : "Delete"}
                      </button>
                    </div>
                  </div>
                </div>
              )
            )}
        </section>
      </main>
    </div>
  );
}

export default App;