PROFILE := "debug"
TARGET := $(shell rustc -vV | sed -n 's|host: ||p')

.DEFAULT_GOAL := target/debug/skytemple-randomizer
.PHONY: clean run

build/*: requirements.txt pyoxidizer.bzl build.rs
	CARGO_MANIFEST_DIR=. \
    PROFILE=$(PROFILE) \
    TARGET=$(TARGET) \
    OUT_DIR=target/out \
    pyoxidizer run-build-script build.rs
	# no idea why we have to do this manually
	mkdir -p target
	cp -r build/$(TARGET) target/out

target/debug/skytemple-randomizer: build/* Cargo.lock Cargo.toml
	PYOXIDIZER_ARTIFACT_DIR=$(shell pwd)/target/out \
    PYO3_CONFIG_FILE=$(shell pwd)/target/out/pyo3-build-config-file.txt \
    cargo build \
      --no-default-features \
      --features "build-mode-prebuilt-artifacts global-allocator-jemalloc allocator-jemalloc"

run: target/debug/skytemple-randomizer
	PYOXIDIZER_ARTIFACT_DIR=$(shell pwd)/target/out \
    PYO3_CONFIG_FILE=$(shell pwd)/target/out/pyo3-build-config-file.txt \
    cargo run \
      --no-default-features \
      --features "build-mode-prebuilt-artifacts global-allocator-jemalloc allocator-jemalloc"

clean:
	rm -rf build
	rm -rf target
	pyoxidizer cache-clear
