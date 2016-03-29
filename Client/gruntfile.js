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
    subgrunt: {
      maze: {
        projects: {
          '../Content/MAZE': 'default'
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
        expand: true,
        cwd: "../Content/MAZE/src",
        src: "**",
        dest: "target/content/maze"
      }
    }
  });

  // Load plugins
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.loadNpmTasks('grunt-subgrunt');
  grunt.loadNpmTasks('grunt-serve');

  // Tasks
  grunt.registerTask('default', ['clean', 'subgrunt', 'copy', 'coffee']);
  grunt.registerTask('run', ['default', 'serve']);
};
