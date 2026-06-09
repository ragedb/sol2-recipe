from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os


class Sol2Conan(ConanFile):
    name = "sol2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ThePhD/sol2"
    description = "a C++ <-> Lua API wrapper with advanced features and top notch performance"
    topics = ("lua", "c++", "bindings")
    settings = "os", "arch", "compiler", "build_type"
    license = "MIT"
    package_type = "header-library"
    no_copy_source = True

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15.7" if Version(self.version) < "3.3.0" else "16",
            "msvc": "191" if Version(self.version) < "3.3.0" else "192",
            "clang": "6",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warning("sol2 requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"sol2 requires C++17 or higher support standard. "
                f"{self.settings.compiler} {self.settings.compiler.version} is not supported."
            )

    def package_id(self):
        self.info.clear()
        
    def requirements(self):
        self.requires("luajit/2.1.0-beta3-2023-01-04")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sol2")
        self.cpp_info.set_property("cmake_target_name", "sol2::sol2")
        self.cpp_info.defines.append("SOL_USING_CXX_LUA_JIT=1")
        self.cpp_info.requires = ["luajit::luajit"]
