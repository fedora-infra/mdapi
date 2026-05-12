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
	var lglvtext, location, hostname, protocol, servname, port *string
	var database, dispense *flag.FlagSet
	var dtbsArgs, dspnArgs []string

	lglvtext = flag.String("loglevel", "info", "Set the application loglevel")
	location = flag.String("location", config.DBFOLDER, "Set the database location")
	flag.Parse()

	config.DBFOLDER = *location

	database = flag.NewFlagSet("database", flag.ExitOnError)
	dispense = flag.NewFlagSet("dispense", flag.ExitOnError)
	hostname = dispense.String("hostname", config.HOSTNAME, "Network hostname for the application server")
	protocol = dispense.String("protocol", config.PROTOCOL, "Network protocol for the application server")
	servname = dispense.String("servname", config.SERVNAME, "Network identity for the application server")
	port = dispense.String("port", "8080", "Network port for the application server")
	config.MakeLogger(lglvtext)

	if flag.NArg() < 1 {
		slog.Log(context.Background(), slog.LevelError, "Invalid subcommand - Expected either 'database' or 'dispense' subcommand")
		os.Exit(1)
	}

	switch flag.Arg(0) {
	case "database":
		for i, arg := range os.Args {
			if arg == "database" && i+1 < len(os.Args) {
				dtbsArgs = os.Args[i+1:]
				break
			}
		}
		expt = database.Parse(dtbsArgs)
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
		for i, arg := range os.Args {
			if arg == "dispense" && i+1 < len(os.Args) {
				dspnArgs = os.Args[i+1:]
				break
			}
		}
		expt = dispense.Parse(dspnArgs)
		if expt != nil {
			slog.Log(context.Background(), slog.LevelError, expt.Error())
			os.Exit(1)
		}
		config.HOSTNAME, config.PROTOCOL, config.SERVNAME = *hostname, *protocol, *servname
		expt = option.Dispense(port)
		if expt != nil {
			slog.Log(context.Background(), slog.LevelError, fmt.Sprintf("Error occurred. %s.", expt.Error()))
			os.Exit(1)
		}
		os.Exit(0)
	default:
		slog.Log(context.Background(), slog.LevelError, "Invalid subcommand - Expected either 'database' or 'dispense' subcommand")
		os.Exit(1)
	}
}
