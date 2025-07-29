.PHONY: make
make:
	@echo "Building binaries..."
	@go build -o meta main.go

.PHONY: lint
lint:
	@echo "Analyzing codebase..."
	@go vet ./...
	@echo "Formatting codebase..."
	@go fmt ./...
	@echo "Checking styles..."
	@go install honnef.co/go/tools/cmd/staticcheck@latest
	@$$(go env GOPATH)/bin/staticcheck ./...
	@echo "Securing codebase..."
	@go install github.com/securego/gosec/v2/cmd/gosec@latest
	@$$(go env GOPATH)/bin/gosec -exclude-generated ./...

.PHONY: test
test:
	@echo "Running testcases..."
	@go test -coverpkg ./metasource/... -coverprofile=coverage.out ./test
	@echo "Generating overview coverage report..."
	@go tool cover -func=coverage.out
	@echo "Generating detailed coverage report..."
	@go tool cover -html coverage.out -o index.html
	@echo "Checking coverage threshold limit..."
	@go tool cover -func=coverage.out | awk '/total:/ { if ($$3+0 < 94.2) { print "Coverage " $$3 " fails threshold 94.2%"; exit 1 } else { print "Coverage " $$3 " meets threshold 94.2%"; exit 0 } }'

.PHONY: wipe
wipe:
	@echo "Cleaning files..."
	@rm -f meta coverage.out index.html

.PHONY: cook
cook:
	@echo "Building image..."
	@podman build --security-opt label=disable --tag t0xic0der/metasource:latest .

.PHONY: chow
chow:
	@echo "Starting container..."
	@podman run --security-opt label=disable --publish 8080:8080 --volume /var/tmp/xyz:/db t0xic0der/metasource:latest -loglevel info -location /db dispense

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make - Build binaries"
	@echo "  lint - Analyze codebase"
	@echo "  test - Run testcases"
	@echo "  wipe - Clean files"
	@echo "  cook - Build image"
	@echo "  chow - Start container"
	@echo "  help - Show documentation"
