# Contributing to ROBOTO_ORIGIN

Thank you for your interest in contributing to ROBOTO_ORIGIN! This document provides guidelines and instructions for contributing to the project.

## Important Note About Repository Structure

**The `roboto_origin` repository is a snapshot-only repository.**

This repository serves as a daily-updated aggregation snapshot of all sub-repositories. It is designed to provide users with a complete, ready-to-use codebase without requiring additional submodule initialization.

### What This Means for Contributors

- **DO NOT** submit module-level pull requests or issues to `roboto_origin`
- **DO** submit module-level contributions to the specific sub-repository where your changes belong
- **DO** use `roboto_origin` Issues and Pull Requests only for aggregation-layer maintenance, such as snapshot sync problems, root documentation, links, repository metadata, or sync workflow fixes
- The main repository will automatically update its snapshot from sub-repositories

## How to Contribute

### 1. Identify the Correct Sub-Repository

Review the module descriptions below to determine which sub-repository your contribution should target:

| Sub-Repository                                                            | Purpose                    | Contribution Topics                                                                      |
| ------------------------------------------------------------------------- | -------------------------- | ---------------------------------------------------------------------------------------- |
| **[rpo_hardware](https://github.com/Roboparty/rpo_hardware)**             | Hardware design files      | Mechanical structures, CAD drawings, PCB designs, BOM improvements                       |
| **[roboparty_deploy](https://github.com/Roboparty/roboparty_deploy)**     | ROS2 deployment framework  | Driver development, middleware modules, deployment configurations, IMU/motor integration |
| **[roboparty_train](https://github.com/Roboparty/roboparty_train)**       | IsaacLab training workflow | RL algorithms, training environments, simulation configs, Sim2Sim transfer               |
| **[rpo_description](https://github.com/Roboparty/rpo_description)**       | URDF robot models          | Kinematic/dynamic descriptions, visual/collision meshes, joint parameters                |
| **[roboparty_firmware](https://github.com/Roboparty/roboparty_firmware)** | Firmware module            | Embedded software, USB2CAN, OrangePi/RDK build tooling, system daemon management         |
| **[rpo_appearance](https://github.com/Roboparty/rpo_appearance)**         | Appearance design files    | Exterior shell design, appearance structure, visual references, surface and assembly notes |
| **[roboparty_navigation](https://github.com/Roboparty/roboparty_navigation)** | Navigation application | Navigation, localization, and related ROS2 application modules                           |
| **[roboparty_xr_teleop](https://github.com/Roboparty/roboparty_xr_teleop)** | XR teleoperation application | XR teleoperation UI, streaming, and robot control integration                          |

### 2. Fork and Clone the Target Sub-Repository

```bash
# Fork the sub-repository on GitHub, then clone it
git clone https://github.com/YOUR_USERNAME/<sub-repo-name>.git
cd <sub-repo-name>

# Add upstream remote
git remote add upstream https://github.com/Roboparty/<sub-repo-name>.git
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-fix-name
```

### 4. Make Your Changes

- Write clean, documented code following the repository's existing style
- Add tests if applicable
- Update documentation as needed
- Commit your changes with clear, descriptive messages

### 5. Submit a Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a pull request on the sub-repository's GitHub page.

## Contribution Guidelines

### Code Quality

- Follow existing code style and conventions in each sub-repository
- Write meaningful commit messages
- Add comments for complex logic
- Test your changes thoroughly before submitting

### Documentation

- Update relevant documentation when making changes
- Include usage examples for new features
- Document API changes in code comments

### Issue Reporting

Use `roboto_origin` Issues only for aggregation-layer problems:

- snapshot sync failures
- missing or outdated module snapshots
- root README, documentation, or link issues
- license, community, or repository metadata issues
- sync script and aggregation workflow problems

For module-level bugs or feature requests, report them in the corresponding sub-repository.

When reporting bugs or requesting features:

1. Navigate to the appropriate sub-repository's Issues tab
2. Search existing issues to avoid duplicates
3. Use clear, descriptive titles
4. Provide detailed information:
   - Environment details (OS, software versions)
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Relevant logs or screenshots

### License

New contributions made directly to the `roboto_origin` aggregation layer are accepted under GNU GPL version 3 unless the target file states otherwise. Module-level contributions must be submitted to the corresponding source repository and follow that repository's applicable contribution and license terms. This applies prospectively and does not relicense existing module snapshots or third-party material. See [LICENSES.md](LICENSES.md).

## Development Workflow

### For Users

If you want to use or build upon the ROBOTO_ORIGIN project:

1. Clone this repository:
   ```bash
   git clone https://github.com/Roboparty/roboto_origin.git
   ```

2. All code is immediately available - no submodule initialization needed

3. Navigate to individual modules in `modules/` directory

4. Follow README instructions in each module

## Community Guidelines

- Be respectful and constructive in all interactions
- Welcome new contributors and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

For detailed community guidelines, please refer to our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Help

- **QQ Group:** 1078670917
- **Email:** tech@roboparty.com
- **GitHub Issues:** Post in the appropriate sub-repository

## Recognition

Contributors who make significant improvements will be recognized in the project documentation. Thank you for helping make ROBOTO_ORIGIN better!

---

**Remember:** Module-level contributions must be made to the specific sub-repositories. The main snapshot repository should only receive aggregation-layer maintenance changes.
