# Refactoring to a Modular Architecture

## Document purpose

This document defines a staged refactoring strategy for replacing the current rigid, manager-heavy structure with a modular architecture based on SOLID, the Single Responsibility Principle, explicit dependency boundaries, component-based Qt Quick UI construction, and feature-sliced ownership.

This is an architecture and migration guide only. It intentionally does not prescribe a big-bang rewrite and does not include implementation changes. Every phase is designed to keep the application runnable, preserve the existing QML-facing behavior, and make rollback possible.

The proposed target paths intentionally follow the requested conventions: shared UI assets in `src/ui/assets/`, shared UI styles in `src/ui/styles/`, application screens in `src/ui/pages/`, shared application components in `src/ui/component/`, general-purpose application services in `src/services/`, and startup composition in a dedicated main bootstrap module.

## Current-state assessment

The codebase already has early feature folders, controllers, and services, but the effective runtime architecture is still centralized. `src/app/shell/app_controller.py` is approximately 1,288 lines and acts as a god facade. It exposes a large QML API while also coordinating file operations, macros, history, Power BI relationships, dialogs, persistence paths, status messages, navigation, and model updates. This creates high coupling, makes regressions likely, and forces unrelated changes into the same class.

The UI has the same problem. `src/app/ui/qml/App.qml` is approximately 738 lines and contains the shell, pages, panels, dialogs, editor, status bar, local state adapters, style tokens, and several inline component definitions. The file is both the composition root and the implementation of most visible UI behavior. A change to one panel can therefore affect the whole application.

The existing `features/` layer is not yet isolated. Multiple feature services import models from `app.ui`, while UI models import types from feature packages. This produces bidirectional dependencies. `FileListModel` is used as both a Qt presentation adapter and the application's mutable document store, so domain and feature logic cannot be tested without Qt.

Several classes remain broader than their names suggest. `visual_editor_service.py` combines catalog filtering, path resolution, type conversion, PBIR encoding, mutation, and display formatting. `filter_controller.py` combines draft editing, persistence, matching, and direct model mutation. `search_controller.py` combines search state, navigation, previews, and replacement operations. The smoke test is embedded in `src/app/ui/application.py`, while the existing `src/app/bootstrap/dependency_container.py` is not the actual composition root.

The project also contains placeholder UI modules under `src/app/ui/pages/` and `src/app/ui/widgets/`, but these are not wired into the QML application. They should not become a second UI implementation. The refactor should replace placeholders with one coherent component system rather than preserve both approaches.

## Architectural goals and non-goals

The primary goal is to make each module changeable for one clear reason. UI components should own presentation, feature slices should own use cases, domain objects should own business rules, infrastructure adapters should own external integration, and the bootstrap layer should be the only place that knows how the complete application is assembled.

The design applies SRP by separating orchestration, business rules, persistence, presentation, and framework integration. It applies the Open/Closed Principle by replacing growing conditional dispatchers, such as the macro step chain, with registries and handlers. It applies the Liskov Substitution Principle by defining small behavioral contracts that test doubles and adapters can satisfy. It applies Interface Segregation by avoiding broad manager interfaces and exposing narrow ports for document access, dialogs, storage, navigation, and status reporting. It applies Dependency Inversion by making feature logic depend on protocols or abstractions rather than Qt models, file-system implementations, or the global application controller.

The target is not a literal copy of Angular. Angular is a useful organizational analogy for colocating markup, logic, and styles, but Qt Quick and Python should still be used idiomatically. QML remains the markup language, JavaScript is limited to local presentation helpers, Python owns feature and domain behavior, and QML-facing adapters expose explicit properties, signals, and slots.

The refactor must not alter user-visible behavior, PBIR mutation safety rules, persisted filter and macro formats, control identifiers, environment-variable behavior, or packaging output unless a migration step explicitly includes compatibility handling. It must not introduce a service locator, a second global controller, or a collection of renamed manager classes. It must not move all logic into QML, and it must not split files merely to reduce line counts without establishing meaningful ownership boundaries.

## Target architecture

The architecture should be organized around dependency direction rather than framework type alone. The proposed top-level structure is:

```text
src/
├── main.py
├── bootstrap/
│   ├── app_bootstrap.py
│   ├── dependency_container.py
│   └── qml_registration.py
├── entities/
│   ├── document/
│   ├── filter/
│   ├── macro/
│   └── powerbi/
├── features/
│   ├── file_management/
│   ├── filters/
│   ├── folder_import/
│   ├── history/
│   ├── editor/
│   ├── macros/
│   ├── search_replace/
│   ├── suggestions/
│   └── visual_editor/
├── services/
│   ├── documents/
│   ├── filesystem/
│   ├── text/
│   ├── dialogs/
│   └── configuration/
├── infrastructure/
│   ├── filesystem/
│   ├── persistence/
│   ├── qt/
│   └── packaging/
└── ui/
    ├── assets/
    │   ├── icons/
    │   ├── fonts/
    │   └── images/
    ├── styles/
    │   ├── Theme.qml
    │   ├── Typography.qml
    │   ├── Spacing.qml
    │   ├── theme_tokens.py
    │   ├── qmldir
    │   └── vscode.qss
    ├── component/
    │   ├── app/
    │   │   └── App/
    │   ├── primitives/
    │   │   ├── ChromeButton/
    │   │   ├── IconButton/
    │   │   ├── PanelButton/
    │   │   ├── PanelTitle/
    │   │   ├── Field/
    │   │   ├── DarkCombo/
    │   │   └── DiffChip/
    │   └── shell/
    │       ├── StatusBar/
    │       └── PanelsSidebar/
    └── pages/
        ├── FilePickerPage/
        └── WorkspacePage/
```

`src/main.py` should contain only the process entry point and delegate immediately to `bootstrap.app_bootstrap`. The `bootstrap/` package is the composition root. The `entities/` package contains stable domain concepts and must not import Qt, QML, controllers, feature packages, or infrastructure implementations. The `features/` package contains independently changeable user capabilities. The `services/` package contains general logic that is genuinely shared across multiple features. The `infrastructure/` package contains concrete adapters for the file system, persistence, Qt framework integration, and packaging/runtime concerns. The `ui/` package contains the root app component, application pages, shared visual components, global styles, and static assets.

A feature slice may use a smaller internal structure when it is simple, but the preferred shape for a non-trivial feature is:

```text
src/features/<feature_name>/
├── domain/
│   ├── models.py
│   └── rules.py
├── application/
│   ├── commands.py
│   ├── queries.py
│   ├── ports.py
│   └── service.py
├── infrastructure/
│   └── adapters.py
├── presentation/
│   ├── controller.py
│   ├── models.py
│   └── component/
│       └── <FeatureComponent>/
│           ├── <FeatureComponent>.qml
│           ├── <FeatureComponent>Logic.js
│           └── <FeatureComponent>Style.qml
└── public.py
```

This internal layering is not permission to create empty folders. A slice should start with only the modules it needs and grow toward this shape as responsibilities become real. `public.py` is the slice's explicit public API; code outside the slice should not import its internal modules.

The allowed dependency direction is:

```text
main → bootstrap → ui/presentation → feature application → entities
                         │                    │
                         └──────── ports ─────┘
                                      ↑
                              infrastructure adapters
```

Python dependency rules apply at sub-layer level. Entity and feature application modules must never import UI, Qt presentation models, or concrete infrastructure. Feature presentation QML may import only the designated shared primitives and global style QML modules; it must not import application pages, the root App module, shell composition, or another feature's private presentation. Infrastructure may implement application ports, but application logic must not import concrete infrastructure classes. The bootstrap module connects both sides.

The QML module layout must be fixed before extraction begins. Module URIs should mirror the requested physical tree under `src/`, so one engine import root can resolve them consistently.

| QML URI | Physical module root and `qmldir` |
|---|---|
| `ui.styles` | `src/ui/styles/qmldir` |
| `ui.component.primitives` | `src/ui/component/primitives/qmldir` |
| `ui.component.shell` | `src/ui/component/shell/qmldir` |
| `ui.pages` | `src/ui/pages/qmldir` |
| `ui.component.app` | `src/ui/component/app/qmldir` |
| `features.<feature_name>.presentation` | `src/features/<feature_name>/presentation/qmldir` |

Each module-level `qmldir` maps public types to nested component paths; component-internal style types remain internal. Bootstrap calls `engine.addImportPath(resource_locator.source_root())`, where the returned directory is the logical `src/` root in both development and the packaged executable, and then loads `App` with `loadFromModule("ui.component.app", "App")`. The resource locator may resolve different physical roots in development and PyInstaller mode, but QML URIs, case, module versions, and logical paths remain identical. Components must not use parent-directory traversal to locate another module.

## UI component standard

Every unique UI element should live in its own named folder and use the same three-file contract. Shared low-level elements live under `src/ui/component/primitives/<ComponentName>/`, shell elements under `src/ui/component/shell/<ComponentName>/`, and the root application component under `src/ui/component/app/App/`. Complete application screens live under `src/ui/pages/<PageName>/`. Components used only by one feature remain inside that feature at `src/features/<feature>/presentation/component/<ComponentName>/` so that feature ownership is not lost.

The three files have distinct responsibilities:

| File | Responsibility | Must not contain |
|---|---|---|
| `<Name>.qml` | Declarative structure, bindings, accessibility metadata, signal wiring, composition of child components, and QML `State`, `Transition`, `Behavior`, and animation objects that target local IDs | Business rules, persistence, file access, large JavaScript functions, duplicated theme constants |
| `<Name>Logic.js` | Small stateless presentation helpers, local formatting, index mapping, and UI-only calculations | Domain mutation, service lookup, global state, direct file-system access, controller construction |
| `<Name>Style.qml` | A component-internal `QtObject` containing component-local visual tokens, dimensions, color variants, and animation durations derived from global style tokens | Feature logic, application state, target-ID-dependent QML states or transitions, duplicated global palette definitions |

A representative shared component is:

```text
src/ui/component/primitives/PanelButton/
├── PanelButton.qml
├── PanelButtonLogic.js
└── PanelButtonStyle.qml
```

A representative page is:

```text
src/ui/pages/WorkspacePage/
├── WorkspacePage.qml
├── WorkspacePageLogic.js
└── WorkspacePageStyle.qml
```

A representative feature-owned component is:

```text
src/features/search_replace/presentation/component/SearchPanel/
├── SearchPanel.qml
├── SearchPanelLogic.js
└── SearchPanelStyle.qml
```

The `Logic.js` and `Style.qml` suffixes are deliberate. `PanelButtonStyle.qml` is a valid local QML type name, while a dotted filename such as `PanelButton.style.qml` is not automatically exposed as `PanelButtonStyle`. The markup imports its sibling JavaScript file with an alias and instantiates its sibling style `QtObject` internally. A `qmldir` file belongs at each QML module root, not inside each component folder, and maps only public component types to their nested paths. This preserves exactly three files inside each component folder while keeping QML module discovery explicit.

`src/ui/styles/` is the source for global palette, typography, spacing, elevation, animation duration, focus, and interaction-state tokens. Component style files consume those tokens and may define only component-specific values. Theme values needed by both QML and Python presentation code should come from one immutable theme-token source, represented by `theme_tokens.py` and registered as a read-only QML singleton; `Theme.qml` can provide QML-friendly semantic aliases. The syntax highlighter receives the same token source through explicit injection rather than hard-coding a second palette.

The existing `vscode.qss` should remain only for Qt widget-based or explicitly non-native dialogs. It cannot style native operating-system dialogs and does not style QML. Startup must continue to use `QApplication`, not `QGuiApplication`, while `QFileDialog`, `QStyleFactory`, or widget QSS remain in use.

`src/ui/assets/` owns reusable icons, fonts, and images. Assets must be referenced through stable resource or module paths rather than file paths calculated relative to an individual component, and packaging must include this directory. Establishing the asset architecture does not require replacing the current letter-based navigation controls; any icon redesign should be a separately approved visual change with accessibility and visual acceptance criteria.

Pages are composition units, not business-logic containers. A page may arrange feature components, bind them to explicitly injected presentation adapters, and coordinate page-level navigation. It should not perform persistence, parse documents, run filters, or directly mutate the global document collection. The initial target preserves the current two top-level states: `FilePickerPage` and `WorkspacePage`. The editor remains a feature component inside `WorkspacePage`; introducing a separately navigable `EditorPage` would be a product behavior change and is outside this refactor.

The root `src/ui/component/app/App/` component should contain only application-shell composition: the top-level window, page host, global overlays, shell-level navigation, status surface, and feature presentation adapters supplied by bootstrap. It must not absorb feature behavior as the current `App.qml` does.

Component APIs should be explicit. Required runtime collaborators are declared as typed `required property` values on the root App or consuming component, passed downward through properties, and never discovered by name. Outputs use signals, and imperative methods are reserved for focus or animation behavior that cannot be represented declaratively. Bootstrap supplies root instances with `QQmlApplicationEngine.setInitialProperties()` or an equivalent initial-property API before loading the root module. Components must not reach upward through root IDs, search for globally named context objects, or read an all-purpose `appController`. QML singletons are reserved for intentionally global, stable, read-only concerns such as theme tokens; feature controllers are not singletons. This prevents hidden dependencies, preserves QML tooling visibility, and permits component-level testing.

## Feature-sliced design rules

Feature-sliced design is used here as an ownership and dependency model, not as a requirement to copy a web framework's directory names exactly. A feature represents a user-recognizable capability such as search and replace, filtering, macros, history, folder import, or visual editing. Everything that exists only to implement that capability should remain in that slice.

The effective layers are described below.

| Layer | Purpose | Examples |
|---|---|---|
| `entities/` | Stable business concepts and rules shared by multiple features | documents, filter definitions, macro definitions, Power BI metadata |
| `features/` | User-facing capabilities and their use cases | search/replace, filters, history, macros, visual editor |
| `services/` | Narrow, reusable application capabilities used by multiple slices | file loading, text search primitives, path resolution, dialog ports, configuration paths |
| `ui/pages/` | Screen-level composition | file picker and workspace pages |
| `ui/component/` | Shared visual building blocks and the application shell | buttons, fields, sidebars, status bar, app root |
| `infrastructure/` | Concrete integration implementations | local file system, JSON persistence, Qt adapters, runtime path resolution |
| `bootstrap/` | Object graph construction and runtime registration | dependency container, QML type/module registration, root property injection |

A feature's domain and application code may import entities and framework-independent service abstractions. Its presentation QML may additionally import `ui.component.primitives` and `ui.styles`, but not `ui.component.app`, `ui.pages`, `ui.component.shell`, or another feature's private presentation module. A feature must not import another feature's private Python modules. When one use case spans multiple features, coordination belongs in a small application-level orchestrator assembled by bootstrap, or it should occur through an explicit published event or narrow public interface. Direct access from macros to filter controller internals or history model internals is forbidden.

The `public.py` module in each feature defines what other layers may use. It can export commands, query interfaces, immutable result types, and presentation-factory functions. It should not expose mutable internal collections or concrete persistence classes.

A module may be promoted from a feature to `services/` or `entities/` only after at least two independent consumers need the same concept and the concept has a stable, feature-neutral name. Premature promotion creates vague shared abstractions. Conversely, copying the same logic across slices to avoid a shared dependency is also prohibited; the correct response is to extract the smallest stable contract.

The current `json_transform` and `json_navigation` folders should not remain top-level feature slices merely because they already exist there. Flattening currently supports document loading and belongs with file management until it has independent consumers. JSON-path-to-line lookup currently supports visual-editor presentation and belongs with that slice until promotion is justified. This keeps the definition of a feature aligned with a user-recognizable capability.

Qt-specific classes belong at the presentation or infrastructure edge. `QAbstractListModel`, `QObject`, signals, slots, and QML property declarations must not appear in entities or core application services. A feature controller may be a `QObject`, but it must delegate use cases to plain Python application classes and convert results into Qt-facing models.

Imports should be mechanically enforceable at package and subpackage level. Static architecture tests should reject `entities → features`, `entities → ui`, `services → ui`, feature domain/application Python importing UI or Qt, private cross-feature imports, feature presentation importing root/pages/shell modules, and concrete infrastructure imports from feature application modules. A separate QML import check should allow feature presentation to import only the shared primitives and styles URIs. Temporary exceptions during migration must be documented, scoped to a specific module, and removed by a named phase.

## Service and domain architecture

`src/services/` must not become the new home for every class ending in `Service`. It is reserved for reusable, framework-independent application capabilities with narrow interfaces and no visual responsibilities. Feature-specific workflows remain inside their feature slice even when their class name contains `Service`.

Top-level `src/infrastructure/` contains concrete adapters shared by multiple slices, while a feature-local `infrastructure/` folder contains an adapter used only by that feature. Dialog ports belong with the application consumer or a shared service contract; the `QFileDialog` implementation belongs in Qt infrastructure. File-system protocols and pure path rules may live under `services/filesystem/`, while local-disk implementations live under `infrastructure/filesystem/`. A Python `Protocol` need not be inherited at runtime, so a shared adapter can satisfy a consumer-owned port structurally and be connected by bootstrap without importing a feature's private module.

The document collection is the most important boundary to introduce first. The current `FileListModel` combines a mutable document repository with a Qt view model. It should be separated into a plain Python `DocumentCollection` abstraction and a Qt list-model adapter. Search, filters, history, macros, folder import, suggestions, and visual editing should depend on a narrow document collection protocol rather than on `FileListModel`.

Suggested general service boundaries are:

| Service boundary | Responsibility | Typical interface shape |
|---|---|---|
| Document reader/writer | Load and save supported documents | `read(path)`, `write(document)` |
| Document collection | Query and update open documents without Qt | `all()`, `get(id)`, `replace(id, content)`, `subscribe(handler)` |
| File-system gateway | Directory scanning and path operations | `scan(path)`, `exists(path)`, `copy(source, target)` |
| Dialog gateway | Ask the user for files or directories | `choose_file()`, `choose_directory()`, `choose_export_path()` |
| Configuration paths | Resolve content and per-user storage paths | `content_root()`, `filters_path()`, `macros_path()` |
| Text search engine | Execute framework-independent text matching | `find(text, query)`, `replace(text, request)` |
| Status publisher | Publish status events without knowing the status bar | `publish(message, severity)` |

Protocols should be small and consumer-owned. A search use case that needs read-only documents should depend on a read-only collection interface, not on the full mutable repository. A filter persistence use case should depend on a filter store interface, not on a generic JSON storage manager. This follows Interface Segregation and keeps tests focused.

The current broad classes should be decomposed by reason for change. `visual_editor_service.py` should separate property catalog/query behavior, path resolution, PBIR value encoding and decoding, type conversion, mutation, and presentation formatting. The filter controller should delegate persistence, matching, and application to separate use cases. The search controller should delegate search execution and replacement commands, retaining only QML-facing state and navigation. The macro conditional dispatcher should become a registry of `MacroStepHandler` implementations so that a new step type does not require editing a central `if/elif` chain.

Controllers should be thin presentation adapters. A controller may validate QML input shape, invoke one command or query, expose observable state, and translate expected failures into presentation messages. It should not open dialogs, resolve environment paths, parse PBIR, write files, coordinate unrelated controllers, or construct dependencies.

Domain mutations should be explicit, but transaction semantics must be defined per use case and must initially preserve characterized behavior. A mutation command should calculate an intended change set and classify each target as applicable, skipped, or failed before commit where practical. PBIR validation failures must never write an invalid target. `Save All` may remain best-effort across independent files, visual editing may apply to valid matching documents while reporting skips, search replacement may preserve its current per-document behavior, and macros may retain step-by-step commits unless a separately approved design introduces rollback. History creation should consume the actual committed change set rather than infer changes by repeatedly snapshotting UI models. No phase may silently convert a best-effort operation into all-or-nothing behavior, or the reverse.

## Bootstrap and dependency composition

Application startup should be centralized in one composition root. `src/main.py` should perform no feature construction and should contain only process-level argument handling followed by a call into `src/bootstrap/app_bootstrap.py`.

`app_bootstrap.py` should create the `QApplication`, load process configuration, construct the dependency container, register QML modules and adapters, supply the root's required initial properties, load `App` from the `ui.component.app` module at `src/ui/component/app/App/App.qml`, and return the process exit code. Smoke-test fixture creation and behavioral assertions must move out of bootstrap into the test suite.

`dependency_container.py` should construct concrete infrastructure adapters first, general services second, feature use cases third, Qt presentation adapters fourth, and the app shell last. Dependencies must be passed through constructors or explicit factory functions. Runtime lookup by string, hidden module singletons, and mutable global registries are not acceptable substitutes for dependency injection.

`qml_registration.py` should register Python-backed QML types, enums, immutable theme tokens, and stable QML module URIs. It should not install runtime feature controllers as global context properties. `app_bootstrap.py` supplies the root App's required runtime instances through initial properties, and the App passes each adapter to the page or feature component that needs it. This rule also applies to the current `syntaxBridge`. During migration, the existing `appController` and `syntaxBridge` context properties may remain as compatibility inputs for the unsplit legacy root, but new components must use explicit properties and must not add new global dependencies.

The bootstrap should also own resource-path decisions. Current paths in `application.py`, `content_locator.py`, `MyApp.spec`, and `tools/build.cmd` depend on specific directory layouts. Those assumptions should be replaced with an injected runtime resource locator before or at the same time as files move. Development mode and packaged mode must use the same logical asset names even when their physical roots differ.

## Current-to-target migration map

The mapping below is directional. It describes intended ownership, not a requirement to move every file in the first phase.

| Current area | Target ownership | Refactoring intent |
|---|---|---|
| `src/app/ui/qml/App.qml` | `src/ui/component/app/App/`, `src/ui/pages/`, shared components, and feature presentation components | Split shell, pages, panels, dialogs, editor, and visual primitives into independently testable components |
| Inline QML colors and dimensions | `src/ui/styles/` plus component-local `<Name>Style.qml` files | Establish one global token system and remove duplicated literals |
| Current letter-based navigation labels and any future icons | `src/ui/assets/icons/` when a separate visual change is approved | Establish a stable packaged asset location without changing the UI as part of this architecture refactor |
| `src/app/ui/file_list_model.py` | Plain document collection in `src/services/documents/` plus a Qt adapter in file-management presentation | Remove Qt from feature and domain logic |
| Other `src/app/ui/*_model.py` files | Their owning feature's `presentation/models.py` | Eliminate the `ui ↔ features` dependency cycle |
| `src/app/shell/app_controller.py` | Feature use cases, shell navigation/status adapters, and temporary compatibility facade | Reduce the facade until it contains no feature business logic, then remove it |
| Macro execution in `app_controller.py` | `src/features/macros/application/runner.py` and step-handler registry | Apply Open/Closed and make each step independently testable |
| History snapshot/diff logic in `app_controller.py` | `src/features/history/application/recorder.py` | Record explicit committed change sets rather than inspect UI state |
| Power BI relationship rebuilding in `app_controller.py` | File-management or Power BI domain service | Isolate document relationship rules from shell presentation |
| `visual_editor_service.py` | Several focused visual-editor application/domain modules | Separate query, conversion, encoding, mutation, and presentation concerns |
| `filter_controller.py` | Thin presentation controller plus filter store, matcher, and apply-filter use cases | Separate UI draft state from persistence and mutation |
| `search_controller.py` | Thin presentation controller plus search query and replacement commands | Separate observable state from algorithms and document writes |
| `src/app/core/content_filter.py` | Filter entities, matcher use case, and persistence adapter | Separate domain data, rules, and storage |
| `src/app/core/file_document.py` and related value objects | `src/entities/document/` | Create a Qt-free document domain |
| General file/text/path helpers | `src/services/filesystem/`, `src/services/text/`, and `src/services/configuration/` | Expose narrow reusable contracts |
| `features/json_transform/flat_json.py` | File-management document loading initially; promote only after independent reuse | Preserve the flattened-JSON contract without treating a technical helper as a user feature |
| `features/json_navigation/` | Visual-editor support initially; promote only after independent reuse | Keep JSON-path line lookup with its current consumer |
| `src/app/ui/json_highlighter.py` and global `syntaxBridge` | Editor presentation plus a Qt highlighter adapter injected explicitly | Preserve document ownership, reattachment, lifecycle, and shared theme colors without a global context object |
| Concrete local storage and Qt dialogs | `src/infrastructure/persistence/`, `src/infrastructure/filesystem/`, and `src/infrastructure/qt/` | Keep framework and I/O details at the edge |
| `src/app/bootstrap/dependency_container.py` | `src/bootstrap/dependency_container.py` | Turn the unused container into the actual composition root |
| Startup logic in `src/app/ui/application.py` | `src/bootstrap/app_bootstrap.py` | Keep UI modules free of process bootstrap and smoke-test logic |
| Smoke test in `application.py` | `test/smoke/` using `test/data/test-project/` | Preserve behavior with an executable test outside production startup |
| Placeholder `ui/pages/*.py` and `ui/widgets/*.py` | Real QML component folders or deletion | Avoid maintaining two competing UI systems |
| Unreferenced `src/app/file-system/` and `src/app/json/` legacy modules | Removal after reference verification | Eliminate misleading, overlapping code; the hyphenated package is not usable through normal import syntax |

The old and new package roots should not be active indefinitely. Temporary re-export modules are acceptable for one migration phase when they preserve imports, but every shim must name its removal phase. No new code may import through a compatibility shim.

## Incremental migration plan

The migration should proceed by dependency seam rather than by directory move. Moving files before breaking coupling would preserve the same architecture under new names.

### Phase 0: Establish a behavioral safety net

First, move the existing smoke-test behavior out of `application.py` and convert it into repeatable tests. Add a QML contract test that checks Qt meta-object properties, signals, slots, model roles and types, dynamically invoked controller methods inside callback bodies, `syntaxBridge.attach`, and full root loading with QML warnings treated as failures. Add focused tests for persisted filters, macro files, search and replace, history, folder import, PBIR page/visual relationships, allowlisted visual mutations, and syntax-highlighter attachment and disposal.

The safety net must explicitly characterize the flattened-JSON contract: escaping of `.`, `[`, `]`, and `\\` in source keys; array index notation; collisions and `FlatJsonCollisionError`; empty objects and arrays; root arrays and primitive roots; duplicate object keys; classification timing; matching against flattened keys; visual-editor path resolution; and the current saved-file shape. It must also resolve the existing folder-import contract discrepancy: runtime code and smoke data currently include generic non-skipped `.json` files, while the README describes a narrower `visual.json` rule and the `allow_loose` parameter is unused. The intended behavior must be decided and locked by tests before refactoring the scanner. Record the current package build command and verify that a packaged smoke launch works.

The exit condition is that the application can be launched, the smoke suite can run without invoking production bootstrap internals, and the current QML-to-controller contract is protected. Refactoring should not begin without this baseline because QML property failures can otherwise appear only at runtime.

### Phase 1: Define boundaries without moving behavior

Introduce the target package skeleton, architectural import tests, small protocols, immutable command/query data types, and a deprecation policy for compatibility shims. Define the global QML theme and resource naming convention. Document feature public APIs and identify an owner for every current model and service.

The exit condition is that dependency rules are executable, target ownership is unambiguous, and no feature is added to the existing `AppController` API.

### Phase 2: Separate the document store from Qt models

Extract a plain Python document collection and define read-only and mutable interfaces according to consumer needs. Keep `FileListModel` as an adapter that observes the collection and translates changes into Qt roles and signals. Migrate one low-risk feature at a time from direct `FileListModel` access to the new interface. Folder import, search, filters, history, suggestions, macros, and visual editing should all reach documents through application ports.

The exit condition is that feature application logic can be unit-tested without constructing a Qt application and no feature application module imports `src.ui` or a Qt list model.

### Phase 3: Decompose uber managers by use case

Extract behavior from `AppController` in vertical slices. Move macro execution to a runner and handler registry, history recording to an explicit change-set consumer, PBIR relationship rebuilding to its domain owner, dialogs behind a dialog port, and path resolution behind configuration services. Split visual editor, filter, and search responsibilities as described earlier. Preserve the existing facade as a forwarding compatibility adapter while QML still depends on it.

Each extraction should follow the same sequence: characterize current behavior with tests, create a narrow application interface, move logic without changing outputs, inject the dependency, forward the old facade method to the new use case, and remove duplicated state. The exit condition is that `AppController` contains only compatibility forwarding plus shell-level navigation/status behavior and has no direct file I/O, persistence, parsing, or feature algorithms.

### Phase 4: Split the QML UI bottom-up

Create `src/ui/styles/` and `src/ui/assets/` first and extract directly into the final `src/ui/...` and feature presentation paths. Every extraction change must also update the resolved QML import root, relevant `qmldir`, `MyApp.spec`, `tools/build.cmd`, and packaged-load smoke test so development and executable builds remain synchronized. Extract the inline primitives from `App.qml` into folders under `src/ui/component/primitives/`, each with markup, logic, and style files. Then extract shell elements, feature panels, and dialogs into their owning modules. Finally, extract page composition into `src/ui/pages/` and reduce the root App component to shell composition.

Components may initially receive the compatibility facade explicitly through a required property where necessary so that visual extraction and controller replacement are not mixed in one change. They must not discover that facade as a new global context dependency. After a component is stable, switch the property to the relevant feature presentation adapter. Visual regression screenshots, keyboard navigation, focus behavior, selection restoration, scroll synchronization, modal behavior, and high-DPI rendering should be checked at every extraction.

The exit condition is that no single QML file implements more than one independently named visual component, the root App component contains no feature implementation, every unique element follows the three-file convention, and global visual tokens are no longer embedded in component markup.

### Phase 5: Activate the composition root

Make `src/bootstrap/dependency_container.py` the real dependency constructor and `app_bootstrap.py` the only application startup path. Register QML types and module URIs through `qml_registration.py`, then supply feature adapter instances as required root properties and pass them downward explicitly. Replace broad `appController` bindings page by page with narrowly scoped feature adapters. Preserve shell-only state, such as the selected page and status notifications, in small shell presentation objects.

The exit condition is that controllers construct no dependencies, no feature locates another feature through a global object, and `AppController` can be removed or reduced to a shell adapter whose name and responsibilities are accurate.

### Phase 6: Normalize remaining Python paths and packaging configuration

After dependency direction is stable, move the remaining Python modules from `src/app/...` into the final `src/...` structure. QML resources, styles, and assets have already moved incrementally with their Phase 4 packaging updates; this phase consolidates Python imports, development scripts, stale packaging entries, and runtime content-path resolution. Introduce temporary import shims only where required to keep intermediate commits runnable.

The exit condition is that development and packaged builds resolve QML, global styles, UI assets, content filters, macros, and user persistence locations through the same logical resource API, with no packaging rule still referencing an obsolete location.

### Phase 7: Remove legacy structure

Delete the old QML monolith, expired import shims, placeholder Python UI files, verified-unreferenced `file-system` and `json` legacy modules, and any controller methods no longer referenced by QML or tests. Remove obsolete packaging entries and update architecture documentation to match the final dependency graph.

The final exit condition is that static architecture tests pass with no exceptions, all compatibility shims are gone, the package build passes, and the old `src/app` layout no longer contains active implementation code.

## Quality gates and verification

Every migration change should satisfy the gates below before the next slice is started.

| Gate | Required evidence |
|---|---|
| Behavioral compatibility | Existing smoke scenarios and feature-focused tests produce the same externally observable results |
| QML contract safety | Meta-object members, dynamic callback invocations, enum values, model roles/types, `syntaxBridge` behavior, and clean-engine QML loading remain compatible |
| Dependency direction | Automated import checks find no forbidden layer direction or private cross-feature import |
| Unit isolation | Feature application tests run without a Qt application, real file dialogs, or writes outside temporary directories |
| UI component quality | Component can be loaded in isolation with test inputs; signals, states, focus, keyboard use, accessibility metadata, and theme variants are verified |
| Data integrity | Each use case follows its documented transaction policy, history receives actual committed change sets, skipped and failed targets remain distinguishable, and invalid PBIR mutations are rejected before writes |
| Persistence compatibility | Existing filter and macro data, IDs, display names, environment variables, and user-storage files remain readable |
| Packaging | PyInstaller includes all QML modules, JavaScript logic files, component style files, global styles, assets, and content data |
| Performance | Large-folder scan, large-file editing, search, filtering, visual-control discovery, and model refresh do not regress beyond an agreed baseline |
| Cleanup | No dead forwarding method, expired shim, unused model, duplicate style token, or duplicate source of truth is introduced |

Line count alone is not a quality gate. A focused module may be large because its cohesive algorithm is substantial, while a small module may still violate boundaries. Review should focus on reasons for change, dependency direction, testability, state ownership, and public API size.

Architecture decisions that affect multiple slices should be captured as short decision records. At minimum, the project should record the document collection contract, the QML component convention, feature public API rules, QML registration strategy, resource location strategy, persistence compatibility policy, and cross-feature coordination mechanism.

## Risks and edge cases

The refactor has several predictable failure modes. They should be handled as architecture constraints rather than discovered late in the migration.

| Risk or edge case | Required mitigation |
|---|---|
| QML silently references a renamed or missing controller member | Protect the current surface with a QML contract test and migrate one component at a time |
| `FileListModel` roles or signal ranges change during adapter extraction | Freeze role names and values initially; add model tests for insert, remove, reset, row updates, selection, and empty collections |
| QML component extraction loses focus, keyboard shortcuts, popup ownership, or scroll synchronization | Add component interaction tests and visual/manual checks before deleting the original block |
| A per-component style file duplicates global theme values | Require component styles to reference `src/ui/styles/` tokens and reject repeated palette literals in review |
| The three-file convention creates empty or meaningless abstractions | Create a named component only for an independently identifiable UI element; keep logic UI-only and concise, but preserve the requested three-file contract once a component exists |
| Feature slices call each other directly and recreate the god object as a feature graph | Coordinate through narrow public contracts, explicit events, or bootstrap-assembled orchestrators; prohibit private cross-feature imports |
| `src/services/` becomes a dumping ground for generic managers | Require two independent consumers, a feature-neutral name, a narrow protocol, and no presentation logic before promotion |
| A new dependency container becomes a service locator | Permit resolution only during bootstrap; pass constructed dependencies explicitly to runtime objects |
| Qt object ownership causes controllers or models to be garbage-collected after injection | Give Qt adapters explicit parents or retain them for the full engine lifetime in the bootstrap-owned container |
| A worker thread emits or mutates Qt models from the wrong thread | Keep model mutation on the Qt GUI thread and marshal background results through queued signals or an explicit dispatcher |
| Transaction behavior changes accidentally during extraction | Characterize each operation separately; preserve best-effort `Save All`, per-document replacement behavior, valid-target/skipped visual edits, and step-wise macro commits unless an approved behavior change says otherwise |
| Macro handlers produce different sequencing, cancellation, or error behavior after extraction | Characterize step ordering, delays, cancellation, unknown step types, missing referenced filters, and the current rule that successful earlier steps remain committed when a later step fails |
| Existing macro `controlId`, filter `id`, or `displayName` values stop resolving | Treat these identifiers as public data contracts and introduce explicit data migration only when unavoidable |
| Visual editor decomposition weakens the allowlist | Keep catalog authorization independent from presentation and require every mutation command to validate its target against the allowlist |
| Flattened JSON changes shape or loses escaped-key semantics | Freeze flattening, collision, root-value, classification, matching, path-resolution, and save-shape behavior before moving document code |
| Folder import is implemented from stale README wording | Resolve the current scanner-versus-README discrepancy and the unused `allow_loose` option with an explicit tested decision |
| Syntax highlighters leak or disappear as editor components are recreated | Give the Qt highlighter clear `QTextDocument` ownership, remove stale retained wrappers, test reattachment/disposal, and inject shared semantic theme colors |
| `content_locator.py` changes behavior when its module moves | Replace `parents[4]` assumptions with an injected resource locator before moving the file |
| QML, JS, styles, or assets work in development but are missing from the executable | Update `MyApp.spec` and `tools/build.cmd` in the same change as every resource move; test the packaged build |
| QML module discovery breaks because of `qmldir` or import URI changes | Define stable QML module URIs, centralize registration, and add a test that loads every page and component from a clean engine |
| QML/JavaScript cache serves stale resources during development | Use stable module versions, avoid duplicate component names across old and new roots, and test from a clean process |
| Native and Qt widget-based dialog styling are conflated | Treat QSS as applicable only to non-native Qt Widgets; preserve and test native dialog behavior separately from QML theming |
| Large model resets cause selection loss or performance regressions | Prefer granular collection events and stable document IDs; restore selection by ID rather than row index |
| Page and visual relationships depend on load order | Make relationship rebuilding deterministic and idempotent, and test missing, duplicated, and out-of-order metadata |
| JSON files are invalid, huge, read-only, deleted externally, or encoded unexpectedly | Define typed application errors, never corrupt the in-memory last-known-good document, and surface actionable status messages |
| User paths contain spaces, Unicode, long names, or network latency | Use `pathlib`, avoid shell string concatenation, maintain cancellation, and test representative Windows paths |
| Two features try to own the same mutable state | Establish one source of truth and provide read models or events; do not mirror dozens of properties in QML as the current `appState` object does |
| Compatibility shims become permanent | Give each shim an owner, removal phase, and test that prevents new imports through it |
| Refactor commits mix behavior changes with moves | Separate characterization, extraction, rewiring, and cleanup so that diffs remain reviewable and rollback remains safe |

The migration should favor deterministic state transitions and stable identifiers. Row numbers, QML object IDs, and display labels must not be used as durable identity when documents, filters, macros, pages, or visuals already have a stable domain identifier.

## Definition of done

The refactor is complete only when the runtime architecture, not merely the folder names, matches this document.

| Area | Completion condition |
|---|---|
| Application shell | The root App component composes pages and shared shell elements but contains no feature implementation |
| UI structure | Every unique UI element has its own folder with markup, logic, and style files; pages are under `src/ui/pages/`; shared app components are under `src/ui/component/` |
| UI resources | Shared assets and style tokens are centralized under `src/ui/assets/` and `src/ui/styles/`, packaged correctly, and free of duplicated global constants |
| Feature ownership | Each user capability is an isolated slice with an explicit public API and no private cross-feature imports |
| Services | `src/services/` contains only narrow, reusable, framework-independent capabilities rather than uber managers |
| Domain | Entities and domain rules are plain Python and have no Qt, QML, controller, storage, or UI imports |
| Presentation | Qt controllers and models are adapters around testable application use cases rather than owners of business behavior |
| Bootstrap | `src/main.py` delegates to one bootstrap module, and the bootstrap/dependency container is the only place that constructs the full object graph |
| App controller | The god facade has been removed, or reduced to a correctly named shell-only adapter with no feature logic |
| Testing | Unit, contract, integration, component, persistence, PBIR safety, and packaged smoke tests pass |
| Compatibility | Existing user files, content data, identifiers, environment variables, and supported workflows continue to work or have an explicit tested migration |
| Legacy cleanup | Old monolithic QML, placeholder UI modules, dead packages, duplicate models, and temporary shims are removed |

The expected outcome is a codebase in which a new feature can be added mostly inside one slice, a new UI element can be developed and tested independently, a service can be replaced through a narrow contract, and the application can be assembled in one visible composition root. Changes should stop propagating through unrelated managers, models, and screens.
