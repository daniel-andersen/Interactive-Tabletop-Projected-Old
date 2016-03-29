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
        port: 9000,
        serve: {
		  path: "target"
		}
      }
	},
    subgrunt: {
      maze: {
        projects: {
          "../Content/MAZE": "default"
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
      maze: {
        files: [
          {expand: true, cwd: "../Content/MAZE/assets", src: "**", dest: "target/content/maze/assets"},
          {expand: true, cwd: "../Content/MAZE/src", src: "**", dest: "target/content/maze/src"},
          {expand: true, cwd: "../Content/MAZE/lib", src: "**", dest: "target/content/maze/lib"},
          {expand: true, cwd: "../Content/MAZE/", src: "*.html", dest: "target/content/maze/"}
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
