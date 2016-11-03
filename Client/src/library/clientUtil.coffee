class ClientUtil
    @uuid: ->
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace /[xy]/g, (c) ->
            r = Math.random() * 16 | 0
            v = if c == 'x' then r else r & 0x3 | 0x8
            return v.toString(16)

    @randomRequestId: -> Math.floor(Math.random() * 1000000)
