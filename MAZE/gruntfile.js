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
    copy: {
      main: {
        expand: true,
        cwd: "../ClientLibrary/src/",
        src: "**",
        dest: "src/"
      }
    },
    connect: {
      server: {
        options: {
          port: 8080,
          base: '',
          keepalive: true
        }
      }
    }
  });

  // Load plugins
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.loadNpmTasks('grunt-contrib-connect');

  // Tasks
  grunt.registerTask('default', ['copy', 'coffee']);
  grunt.registerTask('run', ['default', 'connect']);
};
