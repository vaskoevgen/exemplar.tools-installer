"""
Hidden adversarial acceptance tests for Project Scaffold & Configuration.

These tests target gaps in the visible test suite to catch implementations
that hardcode returns or take shortcuts matching only visible test inputs.
"""
import re
import pytest
from project_scaffold import *


# ─────────────────────────── FilePath ───────────────────────────

class TestGoodhartFilePath:

    def test_goodhart_filepath_dotdot_middle_segment(self):
        """FilePath must reject path traversal sequences embedded within path segments"""
        with pytest.raises(Exception):
            FilePath("src/../etc")
        with pytest.raises(Exception):
            FilePath("a/b/../c")

    def test_goodhart_filepath_standalone_dotdot(self):
        """FilePath must reject '..' as a standalone path"""
        with pytest.raises(Exception):
            FilePath("..")

    def test_goodhart_filepath_single_dot_accepted(self):
        """FilePath should accept a single dot '.' since it matches the regex and doesn't start with / or contain '..'"""
        fp = FilePath(".")
        assert fp.value == "."

    def test_goodhart_filepath_backslash_rejected(self):
        """FilePath must reject Windows-style backslash paths since only POSIX forward slashes are allowed"""
        with pytest.raises(Exception):
            FilePath("src\\main.tsx")

    def test_goodhart_filepath_empty_string_rejected(self):
        """FilePath must reject empty string since it is not a valid file path"""
        with pytest.raises(Exception):
            FilePath("")

    def test_goodhart_filepath_colon_rejected(self):
        """FilePath must reject paths with colons (e.g., Windows drive letters)"""
        with pytest.raises(Exception):
            FilePath("C:/src/main.tsx")

    def test_goodhart_filepath_starts_with_dotdot_slash(self):
        """FilePath must reject paths that start with ../ even if they look relative"""
        with pytest.raises(Exception):
            FilePath("../sibling/file.ts")

    def test_goodhart_filepath_dotdot_at_end(self):
        """FilePath must reject paths ending with /.. """
        with pytest.raises(Exception):
            FilePath("src/components/..")

    def test_goodhart_filepath_space_rejected(self):
        """FilePath must reject paths containing spaces"""
        with pytest.raises(Exception):
            FilePath("src/my file.tsx")

    def test_goodhart_filepath_question_mark_rejected(self):
        """FilePath must reject paths containing question marks"""
        with pytest.raises(Exception):
            FilePath("src/file?.tsx")


# ─────────────────────────── SemVerConstraint ───────────────────────────

class TestGoodhartSemVer:

    def test_goodhart_semver_wildcard_rejected(self):
        """SemVerConstraint must reject wildcard and range specifiers not in the defined format"""
        with pytest.raises(Exception):
            SemVerConstraint("*")
        with pytest.raises(Exception):
            SemVerConstraint(">=1.0.0")
        with pytest.raises(Exception):
            SemVerConstraint("1.x")
        with pytest.raises(Exception):
            SemVerConstraint("1.0.0 - 2.0.0")

    def test_goodhart_semver_or_with_prerelease(self):
        """SemVerConstraint must accept OR-combined constraints with prerelease tags"""
        sv = SemVerConstraint("^1.0.0-alpha.1 || ~2.0.0-beta.2")
        assert sv.value == "^1.0.0-alpha.1 || ~2.0.0-beta.2"

    def test_goodhart_semver_triple_or(self):
        """SemVerConstraint must accept three-way OR constraints"""
        sv = SemVerConstraint("^1.0.0 || ^2.0.0 || ^3.0.0")
        assert "||" in sv.value

    def test_goodhart_semver_no_leading_zero_rejection(self):
        """SemVerConstraint must accept versions with leading zeros in parts (e.g., 0.0.1)"""
        sv = SemVerConstraint("^0.0.1")
        assert sv.value == "^0.0.1"

    def test_goodhart_semver_just_spaces_rejected(self):
        """SemVerConstraint must reject whitespace-only strings"""
        with pytest.raises(Exception):
            SemVerConstraint("   ")

    def test_goodhart_semver_latest_rejected(self):
        """SemVerConstraint must reject the string 'latest'"""
        with pytest.raises(Exception):
            SemVerConstraint("latest")

    def test_goodhart_semver_double_caret_rejected(self):
        """SemVerConstraint must reject malformed constraints like '^^1.0.0'"""
        with pytest.raises(Exception):
            SemVerConstraint("^^1.0.0")


# ─────────────────────────── PackageDependency ───────────────────────────

class TestGoodhartPackageDependency:

    def test_goodhart_package_name_scoped_with_dots(self):
        """PackageDependency must accept scoped packages with dots and underscores"""
        dep = PackageDependency(
            package_name="@types/react-dom",
            version_constraint=SemVerConstraint("^18.0.0"),
            dev=True,
        )
        assert dep.package_name == "@types/react-dom"

    def test_goodhart_package_name_invalid_uppercase_scope(self):
        """PackageDependency must reject scoped names with uppercase in scope"""
        with pytest.raises(Exception):
            PackageDependency(
                package_name="@Types/react",
                version_constraint=SemVerConstraint("^18.0.0"),
                dev=False,
            )

    def test_goodhart_package_name_no_scope_uppercase(self):
        """PackageDependency must reject unscoped names with uppercase"""
        with pytest.raises(Exception):
            PackageDependency(
                package_name="React",
                version_constraint=SemVerConstraint("^18.0.0"),
                dev=False,
            )

    def test_goodhart_package_name_empty_rejected(self):
        """PackageDependency must reject empty package name"""
        with pytest.raises(Exception):
            PackageDependency(
                package_name="",
                version_constraint=SemVerConstraint("^1.0.0"),
                dev=False,
            )

    def test_goodhart_package_name_with_at_but_no_slash(self):
        """PackageDependency must reject scope-like names missing the slash"""
        with pytest.raises(Exception):
            PackageDependency(
                package_name="@scope",
                version_constraint=SemVerConstraint("^1.0.0"),
                dev=False,
            )


# ─────────────────────────── CSSColorValue ───────────────────────────

class TestGoodhartCSSColor:

    def test_goodhart_hex_3_digit(self):
        """CSSColorValue must accept 3-digit hex"""
        assert CSSColorValue("#fff").value == "#fff"

    def test_goodhart_hex_4_digit(self):
        """CSSColorValue must accept 4-digit hex (with alpha)"""
        assert CSSColorValue("#ffff").value == "#ffff"

    def test_goodhart_hex_8_digit(self):
        """CSSColorValue must accept 8-digit hex (with alpha)"""
        assert CSSColorValue("#0a0a0aff").value == "#0a0a0aff"

    def test_goodhart_hex_2_digit_rejected(self):
        """CSSColorValue must reject hex with only 2 digits"""
        with pytest.raises(Exception):
            CSSColorValue("#ff")

    def test_goodhart_hex_9_digit_rejected(self):
        """CSSColorValue must reject hex with 9 digits"""
        with pytest.raises(Exception):
            CSSColorValue("#fffffffff")

    def test_goodhart_no_hash_rejected(self):
        """CSSColorValue must reject hex-like strings without leading '#'"""
        with pytest.raises(Exception):
            CSSColorValue("0a0a0a")
        with pytest.raises(Exception):
            CSSColorValue("ffffff")

    def test_goodhart_named_color_rejected(self):
        """CSSColorValue must reject named CSS colors like 'black'"""
        with pytest.raises(Exception):
            CSSColorValue("black")
        with pytest.raises(Exception):
            CSSColorValue("transparent")


# ─────────────────────────── ViteConfigShape ───────────────────────────

class TestGoodhartViteConfig:

    def test_goodhart_port_3999_rejected(self):
        """ViteConfigShape must reject port 3999 (one below the required 4000)"""
        with pytest.raises(Exception):
            ViteConfigShape(
                plugins=["react()"],
                server_port=3999,
                server_strict_port=True,
                build_out_dir="dist",
                test_config=VitestConfigShape(
                    globals=True, environment="jsdom", setup_files=[], css=True
                ),
            )

    def test_goodhart_port_4001_rejected(self):
        """ViteConfigShape must reject port 4001 (one above the required 4000)"""
        with pytest.raises(Exception):
            ViteConfigShape(
                plugins=["react()"],
                server_port=4001,
                server_strict_port=True,
                build_out_dir="dist",
                test_config=VitestConfigShape(
                    globals=True, environment="jsdom", setup_files=[], css=True
                ),
            )

    def test_goodhart_port_5173_rejected(self):
        """ViteConfigShape must reject Vite's default port 5173"""
        with pytest.raises(Exception):
            ViteConfigShape(
                plugins=["react()"],
                server_port=5173,
                server_strict_port=True,
                build_out_dir="dist",
                test_config=VitestConfigShape(
                    globals=True, environment="jsdom", setup_files=[], css=True
                ),
            )

    def test_goodhart_build_dir_trailing_slash_rejected(self):
        """ViteConfigShape must reject build_out_dir='dist/' with trailing slash"""
        with pytest.raises(Exception):
            ViteConfigShape(
                plugins=["react()"],
                server_port=4000,
                server_strict_port=True,
                build_out_dir="dist/",
                test_config=VitestConfigShape(
                    globals=True, environment="jsdom", setup_files=[], css=True
                ),
            )

    def test_goodhart_build_dir_build_rejected(self):
        """ViteConfigShape must reject build_out_dir='build'"""
        with pytest.raises(Exception):
            ViteConfigShape(
                plugins=["react()"],
                server_port=4000,
                server_strict_port=True,
                build_out_dir="build",
                test_config=VitestConfigShape(
                    globals=True, environment="jsdom", setup_files=[], css=True
                ),
            )


# ─────────────────────────── VitestConfigShape ───────────────────────────

class TestGoodhartVitestConfig:

    def test_goodhart_env_happy_dom_rejected(self):
        """VitestConfigShape must reject 'happy-dom' as environment"""
        with pytest.raises(Exception):
            VitestConfigShape(globals=True, environment="happy-dom", setup_files=[], css=True)

    def test_goodhart_env_node_rejected(self):
        """VitestConfigShape must reject 'node' as environment"""
        with pytest.raises(Exception):
            VitestConfigShape(globals=True, environment="node", setup_files=[], css=True)

    def test_goodhart_env_empty_rejected(self):
        """VitestConfigShape must reject empty string as environment"""
        with pytest.raises(Exception):
            VitestConfigShape(globals=True, environment="", setup_files=[], css=True)


# ─────────────────────────── TSConfigShape ───────────────────────────

class TestGoodhartTSConfig:

    def test_goodhart_target_es2019_rejected(self):
        """TSConfigShape must reject ES2019 (one version below the minimum ES2020)"""
        with pytest.raises(Exception):
            TSConfigShape(
                compiler_target="ES2019",
                jsx="react-jsx",
                strict=True,
                module_resolution="bundler",
                include=["src"],
                types=["vitest/globals"],
            )

    def test_goodhart_target_es2015_rejected(self):
        """TSConfigShape must reject ES2015 (ES6)"""
        with pytest.raises(Exception):
            TSConfigShape(
                compiler_target="ES2015",
                jsx="react-jsx",
                strict=True,
                module_resolution="bundler",
                include=["src"],
                types=["vitest/globals"],
            )

    def test_goodhart_target_es5_rejected(self):
        """TSConfigShape must reject ES5"""
        with pytest.raises(Exception):
            TSConfigShape(
                compiler_target="ES5",
                jsx="react-jsx",
                strict=True,
                module_resolution="bundler",
                include=["src"],
                types=["vitest/globals"],
            )

    def test_goodhart_target_es2025_accepted(self):
        """TSConfigShape must accept future ES2025 target"""
        ts = TSConfigShape(
            compiler_target="ES2025",
            jsx="react-jsx",
            strict=True,
            module_resolution="bundler",
            include=["src"],
            types=["vitest/globals"],
        )
        assert ts.compiler_target == "ES2025"

    def test_goodhart_target_es2030_accepted(self):
        """TSConfigShape must accept far-future ES2030 target"""
        ts = TSConfigShape(
            compiler_target="ES2030",
            jsx="react-jsx",
            strict=True,
            module_resolution="bundler",
            include=["src"],
            types=["vitest/globals"],
        )
        assert ts.compiler_target == "ES2030"

    def test_goodhart_jsx_react_rejected(self):
        """TSConfigShape must reject jsx='react' (old JSX transform)"""
        with pytest.raises(Exception):
            TSConfigShape(
                compiler_target="ES2020",
                jsx="react",
                strict=True,
                module_resolution="bundler",
                include=["src"],
                types=["vitest/globals"],
            )

    def test_goodhart_jsx_preserve_rejected(self):
        """TSConfigShape must reject jsx='preserve'"""
        with pytest.raises(Exception):
            TSConfigShape(
                compiler_target="ES2020",
                jsx="preserve",
                strict=True,
                module_resolution="bundler",
                include=["src"],
                types=["vitest/globals"],
            )

    def test_goodhart_module_resolution_node_rejected(self):
        """TSConfigShape must reject module_resolution='node'"""
        with pytest.raises(Exception):
            TSConfigShape(
                compiler_target="ES2020",
                jsx="react-jsx",
                strict=True,
                module_resolution="node",
                include=["src"],
                types=["vitest/globals"],
            )

    def test_goodhart_module_resolution_nodenext_rejected(self):
        """TSConfigShape must reject module_resolution='nodenext'"""
        with pytest.raises(Exception):
            TSConfigShape(
                compiler_target="ES2020",
                jsx="react-jsx",
                strict=True,
                module_resolution="nodenext",
                include=["src"],
                types=["vitest/globals"],
            )


# ─────────────────────────── PackageJsonShape / Scripts ───────────────────────────

class TestGoodhartPackageJson:

    def test_goodhart_name_close_but_wrong(self):
        """PackageJsonShape must reject names close to but not exactly 'exemplar-tools-docs'"""
        with pytest.raises(Exception):
            PackageJsonShape(
                name="exemplar-tools",
                private=True,
                type="module",
                scripts=PackageJsonScripts(dev="vite", build="tsc && vite build", test="vitest"),
                dependencies=[],
                dev_dependencies=[],
            )

    def test_goodhart_name_underscores_rejected(self):
        """PackageJsonShape must reject name with underscores instead of hyphens"""
        with pytest.raises(Exception):
            PackageJsonShape(
                name="exemplar_tools_docs",
                private=True,
                type="module",
                scripts=PackageJsonScripts(dev="vite", build="tsc && vite build", test="vitest"),
                dependencies=[],
                dev_dependencies=[],
            )

    def test_goodhart_type_commonjs_rejected(self):
        """PackageJsonShape must reject type='commonjs'"""
        with pytest.raises(Exception):
            PackageJsonShape(
                name="exemplar-tools-docs",
                private=True,
                type="commonjs",
                scripts=PackageJsonScripts(dev="vite", build="tsc && vite build", test="vitest"),
                dependencies=[],
                dev_dependencies=[],
            )

    def test_goodhart_scripts_dev_with_flags_rejected(self):
        """PackageJsonScripts must reject dev script with extra flags"""
        with pytest.raises(Exception):
            PackageJsonScripts(dev="vite --port 4000", build="tsc && vite build", test="vitest")

    def test_goodhart_scripts_dev_with_subcommand_rejected(self):
        """PackageJsonScripts must reject dev script 'vite dev'"""
        with pytest.raises(Exception):
            PackageJsonScripts(dev="vite dev", build="tsc && vite build", test="vitest")

    def test_goodhart_scripts_build_semicolon_rejected(self):
        """PackageJsonScripts must reject build script with semicolon instead of &&"""
        with pytest.raises(Exception):
            PackageJsonScripts(dev="vite", build="tsc; vite build", test="vitest")

    def test_goodhart_scripts_build_no_tsc_rejected(self):
        """PackageJsonScripts must reject build script without tsc"""
        with pytest.raises(Exception):
            PackageJsonScripts(dev="vite", build="vite build", test="vitest")

    def test_goodhart_scripts_test_run_rejected(self):
        """PackageJsonScripts must reject test='vitest run' (should be just 'vitest')"""
        with pytest.raises(Exception):
            PackageJsonScripts(dev="vite", build="tsc && vite build", test="vitest run")


# ─────────────────────────── IndexHtmlShape ───────────────────────────

class TestGoodhartIndexHtml:

    def test_goodhart_script_src_jsx_rejected(self):
        """IndexHtmlShape must reject module_script_src ending with .jsx instead of .tsx"""
        with pytest.raises(Exception):
            IndexHtmlShape(
                lang="en",
                google_fonts_links=[],
                root_div_id="root",
                module_script_src="/src/main.jsx",
            )

    def test_goodhart_script_src_no_leading_slash(self):
        """IndexHtmlShape must reject module_script_src without leading slash"""
        with pytest.raises(Exception):
            IndexHtmlShape(
                lang="en",
                google_fonts_links=[],
                root_div_id="root",
                module_script_src="src/main.tsx",
            )

    def test_goodhart_script_src_index_tsx_rejected(self):
        """IndexHtmlShape must reject module_script_src pointing to index.tsx instead of main.tsx"""
        with pytest.raises(Exception):
            IndexHtmlShape(
                lang="en",
                google_fonts_links=[],
                root_div_id="root",
                module_script_src="/src/index.tsx",
            )

    def test_goodhart_root_div_app_rejected(self):
        """IndexHtmlShape must reject root_div_id='app' (common alternative)"""
        with pytest.raises(Exception):
            IndexHtmlShape(
                lang="en",
                google_fonts_links=[],
                root_div_id="app",
                module_script_src="/src/main.tsx",
            )


# ─────────────────────────── MainTsxShape ───────────────────────────

class TestGoodhartMainTsx:

    def test_goodhart_css_import_styles_rejected(self):
        """MainTsxShape must reject css_import='./styles.css'"""
        with pytest.raises(Exception):
            MainTsxShape(
                mount_element_id="root",
                uses_strict_mode=True,
                provider_slots=[],
                css_import="./styles.css",
            )

    def test_goodhart_css_import_no_dot_slash_rejected(self):
        """MainTsxShape must reject css_import='index.css' without './'"""
        with pytest.raises(Exception):
            MainTsxShape(
                mount_element_id="root",
                uses_strict_mode=True,
                provider_slots=[],
                css_import="index.css",
            )

    def test_goodhart_mount_app_rejected(self):
        """MainTsxShape must reject mount_element_id='app'"""
        with pytest.raises(Exception):
            MainTsxShape(
                mount_element_id="app",
                uses_strict_mode=True,
                provider_slots=[],
                css_import="./index.css",
            )


# ─────────────────────────── GoogleFontSpec ───────────────────────────

class TestGoodhartGoogleFont:

    def test_goodhart_display_block_rejected(self):
        """GoogleFontSpec must reject display='block'"""
        with pytest.raises(Exception):
            GoogleFontSpec(family="Inter", weights=[400, 700], italic=False, display="block")

    def test_goodhart_display_auto_rejected(self):
        """GoogleFontSpec must reject display='auto'"""
        with pytest.raises(Exception):
            GoogleFontSpec(family="Inter", weights=[400], italic=False, display="auto")

    def test_goodhart_display_fallback_rejected(self):
        """GoogleFontSpec must reject display='fallback'"""
        with pytest.raises(Exception):
            GoogleFontSpec(family="Inter", weights=[400], italic=False, display="fallback")

    def test_goodhart_display_optional_rejected(self):
        """GoogleFontSpec must reject display='optional'"""
        with pytest.raises(Exception):
            GoogleFontSpec(family="Inter", weights=[400], italic=False, display="optional")


# ─────────────────────────── BgGridUtilitySpec ───────────────────────────

class TestGoodhartBgGrid:

    def test_goodhart_registered_via_css_rejected(self):
        """BgGridUtilitySpec must reject registered_via='css'"""
        with pytest.raises(Exception):
            BgGridUtilitySpec(
                class_name="bg-grid",
                css_property="background-image",
                grid_color="#333",
                grid_size="40px",
                registered_via="css",
            )

    def test_goodhart_registered_via_postcss_rejected(self):
        """BgGridUtilitySpec must reject registered_via='postcss'"""
        with pytest.raises(Exception):
            BgGridUtilitySpec(
                class_name="bg-grid",
                css_property="background-image",
                grid_color="#333",
                grid_size="40px",
                registered_via="postcss",
            )

    def test_goodhart_class_name_not_bg_grid_rejected(self):
        """BgGridUtilitySpec must reject class_name other than 'bg-grid'"""
        with pytest.raises(Exception):
            BgGridUtilitySpec(
                class_name="grid-bg",
                css_property="background-image",
                grid_color="#333",
                grid_size="40px",
                registered_via="tailwind_plugin",
            )


# ─────────────────────────── get_dependency_manifest ───────────────────────────

class TestGoodhartDepManifest:

    def test_goodhart_exact_dep_count(self):
        """get_dependency_manifest must return exactly 14 dependencies (4 prod + 10 dev)"""
        deps = get_dependency_manifest()
        assert len(deps) == 14
        prod = [d for d in deps if not d.dependency.dev]
        dev = [d for d in deps if d.dependency.dev]
        assert len(prod) == 4
        assert len(dev) == 10

    def test_goodhart_no_duplicate_packages(self):
        """get_dependency_manifest must not contain duplicate package names"""
        deps = get_dependency_manifest()
        names = [d.dependency.package_name for d in deps]
        assert len(names) == len(set(names))

    def test_goodhart_convex_is_prod_backend(self):
        """Convex must be a production dependency categorized as BACKEND"""
        deps = get_dependency_manifest()
        convex = [d for d in deps if d.dependency.package_name == "convex"]
        assert len(convex) == 1
        assert convex[0].dependency.dev is False
        assert convex[0].category == DependencyCategory.BACKEND

    def test_goodhart_jsdom_is_dev_testing(self):
        """jsdom must be a dev dependency categorized as TESTING"""
        deps = get_dependency_manifest()
        jsdom = [d for d in deps if d.dependency.package_name == "jsdom"]
        assert len(jsdom) == 1
        assert jsdom[0].dependency.dev is True
        assert jsdom[0].category == DependencyCategory.TESTING

    def test_goodhart_types_react_type_definitions(self):
        """@types/react and @types/react-dom must have TYPE_DEFINITIONS category"""
        deps = get_dependency_manifest()
        types_react = [d for d in deps if d.dependency.package_name == "@types/react"]
        types_react_dom = [d for d in deps if d.dependency.package_name == "@types/react-dom"]
        assert len(types_react) == 1
        assert types_react[0].category == DependencyCategory.TYPE_DEFINITIONS
        assert len(types_react_dom) == 1
        assert types_react_dom[0].category == DependencyCategory.TYPE_DEFINITIONS

    def test_goodhart_tailwind_styling_category(self):
        """tailwindcss must be categorized as STYLING"""
        deps = get_dependency_manifest()
        tw = [d for d in deps if d.dependency.package_name == "tailwindcss"]
        assert len(tw) == 1
        assert tw[0].category == DependencyCategory.STYLING

    def test_goodhart_router_routing_category(self):
        """react-router-dom must be categorized as ROUTING"""
        deps = get_dependency_manifest()
        router = [d for d in deps if d.dependency.package_name == "react-router-dom"]
        assert len(router) == 1
        assert router[0].category == DependencyCategory.ROUTING

    def test_goodhart_vitest_testing_dev(self):
        """vitest must be categorized as TESTING and dev=True"""
        deps = get_dependency_manifest()
        vt = [d for d in deps if d.dependency.package_name == "vitest"]
        assert len(vt) == 1
        assert vt[0].dependency.dev is True
        assert vt[0].category == DependencyCategory.TESTING

    def test_goodhart_tailwind_v3_not_v4(self):
        """Tailwind version constraint must indicate v3.x, not v4"""
        deps = get_dependency_manifest()
        tw = [d for d in deps if d.dependency.package_name == "tailwindcss"][0]
        constraint = tw.dependency.version_constraint.value
        assert constraint.startswith("^3") or constraint.startswith("~3") or constraint.startswith("3")
        assert "4" not in constraint

    def test_goodhart_all_prod_deps_not_dev(self):
        """All four production dependencies must have dev=False"""
        deps = get_dependency_manifest()
        prod_names = {"react", "react-dom", "react-router-dom", "convex"}
        for d in deps:
            if d.dependency.package_name in prod_names:
                assert d.dependency.dev is False, f"{d.dependency.package_name} should be dev=False"

    def test_goodhart_vite_build_tooling(self):
        """vite and @vitejs/plugin-react must be BUILD_TOOLING"""
        deps = get_dependency_manifest()
        vite = [d for d in deps if d.dependency.package_name == "vite"]
        plugin = [d for d in deps if d.dependency.package_name == "@vitejs/plugin-react"]
        assert len(vite) == 1
        assert vite[0].category == DependencyCategory.BUILD_TOOLING
        assert len(plugin) == 1
        assert plugin[0].category == DependencyCategory.BUILD_TOOLING

    def test_goodhart_react_core_framework(self):
        """react and react-dom must be CORE_FRAMEWORK"""
        deps = get_dependency_manifest()
        react = [d for d in deps if d.dependency.package_name == "react"]
        react_dom = [d for d in deps if d.dependency.package_name == "react-dom"]
        assert len(react) == 1
        assert react[0].category == DependencyCategory.CORE_FRAMEWORK
        assert len(react_dom) == 1
        assert react_dom[0].category == DependencyCategory.CORE_FRAMEWORK

    def test_goodhart_typescript_build_tooling_dev(self):
        """typescript must be dev and BUILD_TOOLING"""
        deps = get_dependency_manifest()
        ts = [d for d in deps if d.dependency.package_name == "typescript"]
        assert len(ts) == 1
        assert ts[0].dependency.dev is True
        assert ts[0].category == DependencyCategory.BUILD_TOOLING

    def test_goodhart_all_deps_valid_semver(self):
        """Every dependency must have a version_constraint matching the SemVerConstraint regex"""
        semver_pattern = re.compile(
            r"^[~^]?\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\s*\|\|\s*[~^]?\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?)*$"
        )
        deps = get_dependency_manifest()
        for d in deps:
            assert semver_pattern.match(d.dependency.version_constraint.value), (
                f"{d.dependency.package_name} has invalid semver: {d.dependency.version_constraint.value}"
            )

    def test_goodhart_rationale_non_trivial(self):
        """Every dependency rationale should be meaningfully descriptive (more than a few characters)"""
        deps = get_dependency_manifest()
        for d in deps:
            assert len(d.rationale.strip()) > 5, (
                f"{d.dependency.package_name} has trivial rationale: '{d.rationale}'"
            )

    def test_goodhart_postcss_autoprefixer_present(self):
        """postcss and autoprefixer must both be present as dev dependencies"""
        deps = get_dependency_manifest()
        postcss = [d for d in deps if d.dependency.package_name == "postcss"]
        autoprefixer = [d for d in deps if d.dependency.package_name == "autoprefixer"]
        assert len(postcss) == 1
        assert postcss[0].dependency.dev is True
        assert len(autoprefixer) == 1
        assert autoprefixer[0].dependency.dev is True


# ─────────────────────────── get_style_tokens ───────────────────────────

class TestGoodhartStyleTokens:

    def test_goodhart_font_fallback_chain_lengths(self):
        """Font family tokens must include proper fallback chains, not just primary fonts"""
        tokens = get_style_tokens()
        fonts = tokens.get("fonts") or tokens.get("font_families") or tokens.get("font_tokens")
        # Try common key names
        if fonts is None:
            for k, v in tokens.items():
                if isinstance(v, dict) and "serif" in v:
                    fonts = v
                    break
        assert fonts is not None, "Could not find font tokens in style tokens"
        assert len(fonts["serif"]) >= 2, "serif font list needs fallbacks"
        assert len(fonts["mono"]) >= 2, "mono font list needs fallbacks"
        assert len(fonts["sans"]) >= 3, "sans font list needs fallbacks including system-ui and sans-serif"

    def test_goodhart_font_primary_is_first(self):
        """Font family tokens must have the designated primary font as the first element"""
        tokens = get_style_tokens()
        fonts = None
        for k, v in tokens.items():
            if isinstance(v, dict) and "serif" in v:
                fonts = v
                break
        assert fonts is not None
        assert fonts["serif"][0] == "Instrument Serif"
        assert fonts["mono"][0] == "JetBrains Mono"
        assert fonts["sans"][0] == "Inter"

    def test_goodhart_serif_georgia_fallback(self):
        """Serif font family must include 'Georgia' as an intermediate fallback"""
        tokens = get_style_tokens()
        fonts = None
        for k, v in tokens.items():
            if isinstance(v, dict) and "serif" in v:
                fonts = v
                break
        assert fonts is not None
        assert "Georgia" in fonts["serif"]
        assert "serif" in fonts["serif"]

    def test_goodhart_sans_system_ui_fallback(self):
        """Sans font family must include 'system-ui' as a fallback"""
        tokens = get_style_tokens()
        fonts = None
        for k, v in tokens.items():
            if isinstance(v, dict) and "sans" in v:
                fonts = v
                break
        assert fonts is not None
        assert "system-ui" in fonts["sans"]
        assert "sans-serif" in fonts["sans"]

    def test_goodhart_mono_monospace_fallback(self):
        """Mono font family must include 'monospace' as a fallback"""
        tokens = get_style_tokens()
        fonts = None
        for k, v in tokens.items():
            if isinstance(v, dict) and "mono" in v:
                fonts = v
                break
        assert fonts is not None
        assert "monospace" in fonts["mono"]

    def test_goodhart_body_background_matches_color_token(self):
        """Base body background must match the background color token exactly"""
        tokens = get_style_tokens()
        # Find color tokens and body background
        bg_color = None
        body_bg = None
        for k, v in tokens.items():
            if isinstance(v, dict) and "background" in v:
                bg_color = v["background"]
            if k in ("base_body_background", "body_background", "base_background"):
                body_bg = v
        # At minimum the background color token must be #0a0a0a
        assert bg_color == "#0a0a0a" or body_bg == "#0a0a0a"

    def test_goodhart_return_is_dict(self):
        """get_style_tokens must return a dict"""
        tokens = get_style_tokens()
        assert isinstance(tokens, dict)

    def test_goodhart_utility_classes_list(self):
        """Utility classes in style tokens must be a list containing 'bg-grid'"""
        tokens = get_style_tokens()
        found = False
        for k, v in tokens.items():
            if isinstance(v, list) and "bg-grid" in v:
                found = True
                break
        assert found, "Could not find 'bg-grid' in any list within style tokens"

    def test_goodhart_class_prefixes_list(self):
        """Class prefixes in style tokens must include font-serif, font-mono, font-sans"""
        tokens = get_style_tokens()
        found_prefixes = None
        for k, v in tokens.items():
            if isinstance(v, list) and "font-serif" in v:
                found_prefixes = v
                break
        assert found_prefixes is not None
        assert "font-serif" in found_prefixes
        assert "font-mono" in found_prefixes
        assert "font-sans" in found_prefixes

    def test_goodhart_style_tokens_idempotent(self):
        """get_style_tokens must return identical results on multiple calls (pure function)"""
        t1 = get_style_tokens()
        t2 = get_style_tokens()
        assert t1 == t2


# ─────────────────────────── configure_entry_points edge cases ───────────────────────────

class TestGoodhartConfigureEntryEdge:

    def test_goodhart_font_spec_empty_weights_rejected(self):
        """configure_entry_points must reject GoogleFontSpec with empty weights list"""
        with pytest.raises(Exception) as exc_info:
            font = GoogleFontSpec(family="Inter", weights=[], italic=False, display="swap")
            # If GoogleFontSpec doesn't validate weights, then configure_entry_points must
            configure_entry_points(
                project_root=FilePath("test_project"),
                index_html=IndexHtmlShape(
                    lang="en",
                    google_fonts_links=[],
                    root_div_id="root",
                    module_script_src="/src/main.tsx",
                ),
                main_tsx=MainTsxShape(
                    mount_element_id="root",
                    uses_strict_mode=True,
                    provider_slots=[],
                    css_import="./index.css",
                ),
                index_css=IndexCssShape(
                    tailwind_directives=["@tailwind base", "@tailwind components", "@tailwind utilities"],
                    base_background_color=CSSColorValue("#0a0a0a"),
                    base_text_color=CSSColorValue("#ffffff"),
                    font_face_assignments=[],
                ),
                google_fonts=[font],
            )
        # Should raise invalid_font_spec at some point in the chain

    def test_goodhart_font_spec_empty_family_rejected(self):
        """configure_entry_points must reject GoogleFontSpec with empty family name"""
        with pytest.raises(Exception):
            font = GoogleFontSpec(family="", weights=[400], italic=False, display="swap")
            configure_entry_points(
                project_root=FilePath("test_project"),
                index_html=IndexHtmlShape(
                    lang="en",
                    google_fonts_links=[],
                    root_div_id="root",
                    module_script_src="/src/main.tsx",
                ),
                main_tsx=MainTsxShape(
                    mount_element_id="root",
                    uses_strict_mode=True,
                    provider_slots=[],
                    css_import="./index.css",
                ),
                index_css=IndexCssShape(
                    tailwind_directives=["@tailwind base", "@tailwind components", "@tailwind utilities"],
                    base_background_color=CSSColorValue("#0a0a0a"),
                    base_text_color=CSSColorValue("#ffffff"),
                    font_face_assignments=[],
                ),
                google_fonts=[font],
            )
