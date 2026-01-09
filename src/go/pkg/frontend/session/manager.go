package session

import (
	"net/http"
	"sync"

	"github.com/google/uuid"
)

type Manager struct {
	secret   string
	sessions map[string]*Session
	mu       sync.RWMutex
}

type Session struct {
	ID     string
	CartID string
}

func NewManager(secret string) *Manager {
	return &Manager{
		secret:   secret,
		sessions: make(map[string]*Session),
	}
}

func (m *Manager) GetSession(r *http.Request) *Session {
	cookie, err := r.Cookie("session_id")
	if err != nil {
		return m.createNewSession()
	}

	m.mu.RLock()
	session, exists := m.sessions[cookie.Value]
	m.mu.RUnlock()

	if !exists {
		return m.createNewSession()
	}

	return session
}

func (m *Manager) SetSessionCookie(w http.ResponseWriter, session *Session) {
	http.SetCookie(w, &http.Cookie{
		Name:     "session_id",
		Value:    session.ID,
		Path:     "/",
		HttpOnly: true,
		SameSite: http.SameSiteStrictMode,
	})
}

func (m *Manager) createNewSession() *Session {
	sessionID := uuid.New().String()
	cartID := uuid.New().String()

	session := &Session{
		ID:     sessionID,
		CartID: cartID,
	}

	m.mu.Lock()
	m.sessions[sessionID] = session
	m.mu.Unlock()

	return session
}