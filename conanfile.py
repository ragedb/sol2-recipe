from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class Sol2Conan(ConanFile):
    name = "sol2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ThePhD/sol2"
    description = "a C++ <-> Lua API wrapper with advanced features and top notch performance"
    topics = ("lua", "c++", "bindings")
    settings = "os", "arch", "compiler", "build_type"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15.7" if tools.Version(self.version) < "3.3.0" else "16",
            "clang": "6",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("sol2 requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("sol2 requires C++17 or higher support standard."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler,
                                                    self.settings.compiler.version))


    def package_id(self):
        self.info.header_only()
        
    def requirements(self):
        self.requires("luajit/2.1.0-beta3-2023-01-04")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        extracted_dir = extracted_dir.replace("-luajit", "")
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", src=os.path.join(self._source_subfolder, "include"), dst="include")
        self.copy("*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_info(self):
        self.cpp_info.defines.append("SOL_USING_CXX_LUA_JIT=1")
