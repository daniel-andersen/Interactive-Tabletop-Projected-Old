module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    jshint: {
      files: ['Gruntfile.js', 'src/**/*.js']
    },
    pkg: grunt.file.readJSON('package.json'),
    coffee: {
      coffee_to_js: {
        options: {
          bare: true,
          sourceMap: true
        },
        expand: true,
        flatten: false,
        cwd: "src",
        src: ["**/*.coffee"],
        dest: 'src',
        ext: ".js"
      }
    },
    serve: {
      options: {
        port: 9002,
        serve: {
		  path: "target"
		}
      }
	},
    subgrunt: {
      menu: {
        projects: {
          "../Content/Menu": "default"
        }
      },
      maze: {
        projects: {
          "../Content/MAZE": "default"
        }
      },
      example2: {
        projects: {
          "../Content/Example2": "default"
        }
      },
      example4: {
        projects: {
          "../Content/Example4": "default"
        }
      },
      geometry: {
        projects: {
          "../Content/Geometry": "default"
        }
      }
    },
    clean: ["target"],
    copy: {
      library: {
        expand: true,
        cwd: "src",
        src: "**",
        dest: "target/"
      },
      menu: {
        files: [
          {expand: true, cwd: "../Content/Menu/assets", src: "**", dest: "target/content/Menu/assets"},
          {expand: true, cwd: "../Content/Menu/src", src: "**", dest: "target/content/Menu/src"},
          {expand: true, cwd: "../Content/Menu/lib", src: "**", dest: "target/content/Menu/lib"},
          {expand: true, cwd: "../Content/Menu/", src: "*.html", dest: "target/content/Menu/"}
        ]
      },
      maze: {
        files: [
          {expand: true, cwd: "../Content/MAZE/assets", src: "**", dest: "target/content/maze/assets"},
          {expand: true, cwd: "../Content/MAZE/src", src: "**", dest: "target/content/maze/src"},
          {expand: true, cwd: "../Content/MAZE/lib", src: "**", dest: "target/content/maze/lib"},
          {expand: true, cwd: "../Content/MAZE/", src: "*.html", dest: "target/content/maze/"}
        ]
      },
      example2: {
        files: [
          {expand: true, cwd: "../Content/Example2/assets", src: "**", dest: "target/content/example2/assets"},
          {expand: true, cwd: "../Content/Example2/src", src: "**", dest: "target/content/example2/src"},
          {expand: true, cwd: "../Content/Example2/lib", src: "**", dest: "target/content/example2/lib"},
          {expand: true, cwd: "../Content/Example2/", src: "*.html", dest: "target/content/example2/"}
        ]
      },
      example4: {
        files: [
          {expand: true, cwd: "../Content/Example4/assets", src: "**", dest: "target/content/example4/assets"},
          {expand: true, cwd: "../Content/Example4/src", src: "**", dest: "target/content/example4/src"},
          {expand: true, cwd: "../Content/Example4/lib", src: "**", dest: "target/content/example4/lib"},
          {expand: true, cwd: "../Content/Example4/", src: "*.html", dest: "target/content/example4/"}
        ]
      },
      geometry: {
        files: [
          {expand: true, cwd: "../Content/Geometry/assets", src: "**", dest: "target/content/Geometry/assets"},
          {expand: true, cwd: "../Content/Geometry/src", src: "**", dest: "target/content/Geometry/src"},
          {expand: true, cwd: "../Content/Geometry/lib", src: "**", dest: "target/content/Geometry/lib"},
          {expand: true, cwd: "../Content/Geometry/", src: "*.html", dest: "target/content/Geometry/"}
        ]
      }
    }
  });

  // Load plugins
  grunt.loadNpmTasks("grunt-contrib-clean");
  grunt.loadNpmTasks("grunt-contrib-copy");
  grunt.loadNpmTasks("grunt-contrib-coffee");
  grunt.loadNpmTasks("grunt-subgrunt");
  grunt.loadNpmTasks("grunt-serve");

  // Tasks
  grunt.registerTask("default", ["clean", "coffee", "subgrunt", "copy"]);
  grunt.registerTask("run", ["default", "serve"]);
};
