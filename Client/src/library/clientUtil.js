var ClientUtil;

ClientUtil = (function() {
  function ClientUtil() {}

  ClientUtil.randomRequestId = function() {
    return Math.floor(Math.random() * 1000000);
  };

  return ClientUtil;

})();

//# sourceMappingURL=clientUtil.js.map
