package main

import (
	"context"
	"flag"
	"fmt"
	"log/slog"
	"metasource/metasource/config"
	"metasource/metasource/option"
	"os"
)

func main() {
	var expt error
	var lglvtext, location, port *string
	var database, dispense *flag.FlagSet

	lglvtext = flag.String("loglevel", "info", "Set the application loglevel")
	location = flag.String("location", config.DBFOLDER, "Set the database location")
	flag.Parse()

	config.DBFOLDER = *location

	database = flag.NewFlagSet("database", flag.ExitOnError)
	dispense = flag.NewFlagSet("dispense", flag.ExitOnError)
	port = dispense.String("port", "8080", "Port to run the server on")
	config.SetLogger(lglvtext)

	if flag.NArg() < 1 {
		slog.Log(context.Background(), slog.LevelError, "Invalid subcommand")
		slog.Log(context.Background(), slog.LevelInfo, "Expected either 'database' or 'dispense' subcommand")
		os.Exit(1)
	}

	switch flag.Arg(0) {
	case "database":
		expt = database.Parse(os.Args[2:])
		if expt != nil {
			slog.Log(context.Background(), slog.LevelError, expt.Error())
			os.Exit(1)
		}
		expt = option.Database()
		if expt != nil {
			slog.Log(context.Background(), slog.LevelError, expt.Error())
			os.Exit(1)
		}
		os.Exit(0)
	case "dispense":
		expt = dispense.Parse(os.Args[2:])
		if expt != nil {
			slog.Log(context.Background(), slog.LevelError, expt.Error())
			os.Exit(1)
		}
		expt = option.Dispense(port)
		if expt != nil {
			slog.Log(context.Background(), slog.LevelError, fmt.Sprintf("Error occurred. %s.", expt.Error()))
			os.Exit(1)
		}
	default:
		slog.Log(context.Background(), slog.LevelError, "Invalid subcommand")
		slog.Log(context.Background(), slog.LevelInfo, "Expected either 'database' or 'dispense' subcommand")
		os.Exit(1)
	}
}
