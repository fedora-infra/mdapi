package routes

import (
	"embed"
	"fmt"
	"io/fs"
	"metasource/metasource/config"
	"net/http"
)

//go:embed assets/*
var static embed.FS

func RetrieveStatic(w http.ResponseWriter, r *http.Request) {
	assets, expt := fs.Sub(static, config.ASSETSDB)
	if expt != nil {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusInternalServerError, http.StatusText(http.StatusInternalServerError)), http.StatusInternalServerError)
		return
	}
	http.StripPrefix("/assets/", http.FileServer(http.FS(assets))).ServeHTTP(w, r)
}
