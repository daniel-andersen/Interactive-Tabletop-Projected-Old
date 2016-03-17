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
    }
  });

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.loadNpmTasks('grunt-serve');

  // Default task(s).
  grunt.registerTask('default', ['coffee']);
  grunt.registerTask('run', ['coffee', 'serve']);
};
