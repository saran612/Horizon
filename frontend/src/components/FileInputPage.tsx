import React, { useState, useRef } from 'react';

interface FileWithProgress {
  id: string;
  name: string;
  size: number;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'failed';
  file?: File;
  extractedUuids?: string[];
  generatedMdFiles?: string[];
}

export default function FileInputPage() {
  const [files, setFiles] = useState<FileWithProgress[]>(() => {
    const saved = localStorage.getItem('horizon_uploaded_files');
    return saved ? JSON.parse(saved) : [];
  });
  const [isDragActive, setIsDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const saveToLocalStorage = (list: FileWithProgress[]) => {
    const sanitized = list.map(({ file, ...rest }) => rest);
    localStorage.setItem('horizon_uploaded_files', JSON.stringify(sanitized));
  };

  const processFiles = (newFiles: FileList) => {
    setError(null);

    if (newFiles.length > 1) {
      setError("Only one file can be uploaded at a time.");
      return;
    }

    const file = newFiles[0];
    if (!file) return;

    const allowedExtensions = ['.pdf', '.doc', '.docx'];
    const allowedMimeTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    const isImage = file.type.startsWith('image/');
    const hasAllowedMime = allowedMimeTypes.includes(file.type);
    const hasAllowedExt = allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

    if (!isImage && !hasAllowedMime && !hasAllowedExt) {
      setError("Invalid file type. Only PDF, Word, and Image files are supported.");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError("File size exceeds the 10MB limit.");
      return;
    }

    const fileObj: FileWithProgress = {
      id: `${file.name}-${Date.now()}-${Math.random()}`,
      name: file.name,
      size: file.size,
      progress: 0,
      status: 'pending',
      file,
    };
    
    const updatedList = [fileObj];
    setFiles(updatedList);
    saveToLocalStorage(updatedList);

    // Upload file to backend
    uploadFile(fileObj);
  };

  const uploadFile = (fileObj: FileWithProgress) => {
    if (!fileObj.file) return;
    const formData = new FormData();
    formData.append('file', fileObj.file);

    const xhr = new XMLHttpRequest();
    
    setFiles((prev) => {
      const next = prev.map((f) => (f.id === fileObj.id ? { ...f, status: 'uploading' as const, progress: 0 } : f));
      saveToLocalStorage(next);
      return next;
    });

    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable) {
        const percentComplete = Math.round((event.loaded / event.total) * 100);
        setFiles((prev) => {
          const next = prev.map((f) => (f.id === fileObj.id ? { ...f, progress: percentComplete } : f));
          saveToLocalStorage(next);
          return next;
        });
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          setFiles((prev) => {
            const next = prev.map((f) =>
              f.id === fileObj.id
                ? {
                    ...f,
                    progress: 100,
                    status: 'completed' as const,
                    extractedUuids: response.extracted_uuids,
                    generatedMdFiles: response.generated_md_files,
                  }
                : f
            );
            saveToLocalStorage(next);
            return next;
          });
        } catch (e) {
          setFiles((prev) => {
            const next = prev.map((f) => (f.id === fileObj.id ? { ...f, progress: 100, status: 'completed' as const } : f));
            saveToLocalStorage(next);
            return next;
          });
        }
      } else {
        setError(`Upload failed: ${xhr.statusText || 'Server error'}`);
        setFiles((prev) => {
          const next = prev.map((f) => (f.id === fileObj.id ? { ...f, status: 'failed' as const } : f));
          saveToLocalStorage(next);
          return next;
        });
      }
    });

    xhr.addEventListener('error', () => {
      setError("Network error occurred during upload.");
      setFiles((prev) => {
        const next = prev.map((f) => (f.id === fileObj.id ? { ...f, status: 'failed' as const } : f));
        saveToLocalStorage(next);
        return next;
      });
    });

    xhr.open('POST', 'http://localhost:8000/api/v1/upload');
    xhr.send(formData);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFiles(e.target.files);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  const removeFile = (id: string) => {
    setFiles((prev) => {
      const next = prev.filter((f) => f.id !== id);
      saveToLocalStorage(next);
      return next;
    });
  };

  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  };

  return (
    <div style={styles.container}>
      <div style={styles.logoContainer}>
        <span style={styles.logoText}>Horizon</span>
      </div>

      <header style={styles.header}>
        <h1 style={styles.title}>File Upload Center</h1>
        <p style={styles.subtitle}>Upload, track, and manage your assets with ease.</p>
      </header>

      {error && (
        <div style={styles.errorContainer}>
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#ef4444"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ flexShrink: 0 }}
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span style={styles.errorText}>{error}</span>
        </div>
      )}

      <div
        style={{
          ...styles.dropZone,
          ...(isDragActive ? styles.dropZoneActive : {}),
        }}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*,application/pdf,.doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />

        <div style={styles.uploadIconContainer}>
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--accent)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>

        <p style={styles.dropText}>
          Drag & drop your files here, or{' '}
          <span style={styles.browseLink}>
            browse
          </span>
        </p>
        <p style={styles.supportText}>Supports PDF, Word Documents, and Images</p>
      </div>

      {files.length > 0 && (
        <div style={styles.fileListContainer}>
          <h3 style={styles.listTitle}>Selected Files ({files.length})</h3>
          <div style={styles.fileList}>
            {files.map((fileObj) => (
              <div key={fileObj.id} style={styles.fileItem}>
                <div style={styles.fileIcon}>
                  <svg
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="var(--text)"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                </div>
                
                <div style={styles.fileDetails}>
                  <div style={styles.fileNameRow}>
                    <span style={styles.fileName}>{fileObj.name}</span>
                    <button
                      onClick={() => removeFile(fileObj.id)}
                      style={styles.removeBtn}
                      title="Remove file"
                    >
                      &times;
                    </button>
                  </div>
                  <div style={styles.fileMeta}>
                    <span>{formatBytes(fileObj.size)}</span>
                    <span style={styles.dot}>•</span>
                    <span style={{
                      ...styles.statusText,
                      color: fileObj.status === 'completed' ? '#10b981' : 
                             fileObj.status === 'uploading' ? 'var(--accent)' : 'var(--text)'
                    }}>
                      {fileObj.status.charAt(0).toUpperCase() + fileObj.status.slice(1)}
                    </span>
                  </div>

                  {fileObj.extractedUuids && fileObj.extractedUuids.length > 0 && (
                    <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-h)' }}>Extracted UUIDs:</span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {fileObj.extractedUuids.map(uuid => (
                          <span key={uuid} style={{ fontSize: '11px', padding: '2px 6px', borderRadius: '4px', backgroundColor: 'var(--social-bg)', border: '1px solid var(--border)', color: 'var(--text-h)' }}>
                            {uuid}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {fileObj.status === 'uploading' && (
                    <div style={styles.progressContainer}>
                      <div style={styles.progressBarBg}>
                        <div
                          style={{
                            ...styles.progressBarFill,
                            width: `${fileObj.progress}%`,
                          }}
                        />
                      </div>
                      <span style={styles.progressPercent}>{fileObj.progress}%</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: '100%',
    maxWidth: '640px',
    margin: '40px auto',
    padding: '24px',
    boxSizing: 'border-box',
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  header: {
    textAlign: 'center',
  },
  title: {
    fontSize: '28px',
    fontWeight: '600',
    margin: '0 0 8px 0',
    color: 'var(--text-h)',
  },
  subtitle: {
    fontSize: '15px',
    color: 'var(--text)',
    margin: 0,
  },
  dropZone: {
    border: '2px dashed var(--border)',
    borderRadius: '16px',
    padding: '48px 24px',
    textAlign: 'center',
    cursor: 'pointer',
    backgroundColor: 'var(--social-bg)',
    transition: 'all 0.2s ease-in-out',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
  },
  dropZoneActive: {
    borderColor: 'var(--accent)',
    backgroundColor: 'var(--accent-bg)',
  },
  uploadIconContainer: {
    width: '64px',
    height: '64px',
    borderRadius: '50%',
    backgroundColor: 'var(--accent-bg)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '8px',
  },
  dropText: {
    fontSize: '16px',
    fontWeight: '500',
    color: 'var(--text-h)',
    margin: 0,
  },
  browseLink: {
    color: 'var(--accent)',
    textDecoration: 'underline',
    fontWeight: '600',
  },
  supportText: {
    fontSize: '13px',
    color: 'var(--text)',
    margin: 0,
  },
  fileListContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    textAlign: 'left',
  },
  listTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: 'var(--text-h)',
    margin: 0,
  },
  fileList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  fileItem: {
    display: 'flex',
    gap: '16px',
    padding: '16px',
    borderRadius: '12px',
    border: '1px solid var(--border)',
    backgroundColor: 'var(--bg)',
    boxShadow: 'var(--shadow)',
    alignItems: 'flex-start',
  },
  fileIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '10px',
    borderRadius: '8px',
    backgroundColor: 'var(--social-bg)',
  },
  fileDetails: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    minWidth: 0,
  },
  fileNameRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '12px',
  },
  fileName: {
    fontSize: '14px',
    fontWeight: '600',
    color: 'var(--text-h)',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  removeBtn: {
    background: 'none',
    border: 'none',
    color: 'var(--text)',
    fontSize: '18px',
    cursor: 'pointer',
    padding: '0 4px',
    lineHeight: 1,
    transition: 'color 0.15s ease',
  },
  fileMeta: {
    display: 'flex',
    gap: '8px',
    fontSize: '12px',
    color: 'var(--text)',
    alignItems: 'center',
  },
  dot: {
    color: 'var(--border)',
  },
  statusText: {
    fontWeight: '500',
  },
  progressContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginTop: '4px',
  },
  progressBarBg: {
    flex: 1,
    height: '6px',
    backgroundColor: 'var(--border)',
    borderRadius: '3px',
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: 'var(--accent)',
    borderRadius: '3px',
    transition: 'width 0.2s ease',
  },
  progressPercent: {
    fontSize: '12px',
    fontWeight: '600',
    color: 'var(--text-h)',
    minWidth: '28px',
    textAlign: 'right',
  },
  errorContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '12px 16px',
    borderRadius: '10px',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    textAlign: 'left',
  },
  errorText: {
    fontSize: '14px',
    color: '#ef4444',
    fontWeight: '500',
  },
  logoContainer: {
    position: 'absolute',
    top: '24px',
    left: '24px',
    display: 'flex',
    alignItems: 'center',
    userSelect: 'none',
  },
  logoText: {
    fontSize: '32px',
    fontWeight: '800',
    letterSpacing: '-0.75px',
    color: 'var(--accent)',
    fontFamily: 'var(--sans)',
  },
};
