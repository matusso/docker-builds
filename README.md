# docker-builds

## Security Tools Docker Images

This repository automates the process of building and publishing Docker images for various popular security tools.

## About

This project simplifies the deployment of essential security tools by containerizing them. Using these Docker images, you can quickly run tools without worrying about installation dependencies or conflicts on your host system.

The following security tools are included in this repository:

1. **[binwalk](https://github.com/ReFirmLabs/binwalk)**  
   - A tool for analyzing binary files for embedded files and executable code.  
   - Useful for reverse engineering firmware and binary analysis.
   - [![ghcr.io/matusso/binwalk](https://github.com/matusso/docker-builds/actions/workflows/binwalk.yml/badge.svg)](https://github.com/matusso/docker-builds/actions/workflows/binwalk.yml)

2. **[dirsearch](https://github.com/maurosoria/dirsearch)**  
   - A simple command-line tool designed to brute-force directories and files in web servers.  
   - Helps uncover hidden directories and files for security assessments.
   - [![ghcr.io/matusso/dirsearch](https://github.com/matusso/docker-builds/actions/workflows/dirsearch.yml/badge.svg)](https://github.com/matusso/docker-builds/actions/workflows/dirsearch.yml)

3. **[ghauri](https://github.com/r0oth3x49/ghauri)**  
   - A fast and powerful SQL injection detection and exploitation tool.  
   - Ideal for penetration testing web applications.
   - [![ghcr.io/matusso/ghauri](https://github.com/matusso/docker-builds/actions/workflows/ghauri.yml/badge.svg)](https://github.com/matusso/docker-builds/actions/workflows/ghauri.yml)

4. **[metasploit-framework](https://github.com/rapid7/metasploit-framework)**  
   - A comprehensive penetration testing framework.  
   - Features exploits, payloads, and tools for security testing and research.
   - [![ghcr.io/matusso/metasploit-framework](https://github.com/matusso/docker-builds/actions/workflows/metasploit-framework.yml/badge.svg)](https://github.com/matusso/docker-builds/actions/workflows/metasploit-framework.yml)

5. **[mvt-project](https://github.com/mvt-project/mvt)**  
   - Mobile Verification Toolkit (MVT) for analyzing mobile devices.  
   - Assists in detecting traces of known surveillance spyware.
   - [![ghcr.io/matusso/mvt](https://github.com/matusso/docker-builds/actions/workflows/mvt-project.yml/badge.svg)](https://github.com/matusso/docker-builds/actions/workflows/mvt-project.yml)

6. **[kiterunner](https://github.com/assetnote/kiterunner)**  
   - Kiterunner is a tool that is capable of not only performing traditional content discovery at lightning fast speeds, but also bruteforcing routes/endpoints in modern applications..  
   - [![ghcr.io/matusso/kiterunner](https://github.com/matusso/docker-builds/actions/workflows/kiterunner.yml/badge.svg)](https://github.com/matusso/docker-builds/actions/workflows/kiterunner.yml)

## Multi-Architecture Support

All Docker images are built and published for the following architectures:
- **amd64**: For x86_64 systems.
- **arm64**: For ARM-based systems, including Apple M1/M2 and Raspberry Pi.

## Why Use This Project?

- **Consistency:** Pre-built Docker images ensure that the tools work as intended across various environments.  
- **Convenience:** No need to manually install or configure dependencies for each tool.  
- **Automation:** GitHub Actions automatically build and publish updated Docker images when changes are made to the repository.  

## How to Use

1. Pull the desired tool's Docker image:  
```bash
docker pull ghcr.io/matusso/<tool-name>
```

2. Run the tool:
```bash
docker run --rm -it ghcr.io/matusso/<tool-name> [tool-arguments]  
```

#### Example

To use dirsearch:

```
docker pull ghcr.io/matusso/dirsearch  
docker run --rm -it ghcr.io/matusso/dirsearch -u https://example.com  
```

#### Contributions

Contributions to add more tools or improve the existing ones are welcome. Please create a pull request or open an issue for discussion.


#### License

This repository is distributed under the MIT License. Please check the individual projects for their respective licenses.