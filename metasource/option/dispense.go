package option

import (
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
	"metasource/metasource/routes"
	"net/http"
	"time"
)

func Navigate() http.Handler {
	router := chi.NewRouter()
	router.Use(middleware.Logger)
	router.Use(middleware.Recoverer)
	router.Use(middleware.StripSlashes)
	router.Use(cors.Handler(cors.Options{
		AllowedOrigins: []string{"*"},
		AllowedMethods: []string{"GET"},
		AllowedHeaders: []string{"*"},
	}))

	router.Get("/", routes.RetrieveHome)
	router.Get("/assets/*", routes.RetrieveStatic)
	router.Get("/branches", routes.RetrieveBranches)
	router.Get("/{vers}/changelog/{name}", routes.RetrieveOthr)
	router.Get("/{vers}/pkg/{name}", routes.RetrievePrmy)
	router.Get("/{vers}/files/{name}", routes.RetrieveFileList)
	router.Get("/{vers}/srcpkg/{name}", routes.RetrieveSrce)
	router.Get("/{vers}/{rela}/{name}", routes.RetrieveRelation)

	return router
}

func Dispense(port *string) error {
	server := &http.Server{
		Addr:              ":" + *port,
		Handler:           Navigate(),
		ReadHeaderTimeout: 10 * time.Second,
	}
	return server.ListenAndServe()
}
