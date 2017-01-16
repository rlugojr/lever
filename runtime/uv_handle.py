from rpython.rtyper.lltypesystem import rffi, lltype
from space import *
import rlibuv as uv
import core
import uv_callback

class Handle(Object):
    def __init__(self, handle):
        self.handle = handle
        self.closed = False
        self.buffers = [] # TODO: remove this.

    def getattr(self, name):
        if name == u"active":
            return boolean(uv.is_active(self.handle))
        if name == u"closing":
            return boolean(uv.is_closing(self.handle))
        if name == u"closed":
            return boolean(self.closed)
        if name == u"ref":
            return boolean(uv.has_ref(self.handle))
        return Object.getattr(self, name)

    def setattr(self, name, value):
        if name == u"ref":
            if is_true(value):
                uv.ref(self.handle)
            else:
                uv.unref(self.handle)
            return value
        return Object.setattr(self, name, value)

    # All handles are resources, so I don't think doing
    # automatic close on losing them would do any good.
    # Besides, some handles have to override the .close

@Handle.method(u"close", signature(Handle))
def Handle_close(self):
    response = uv_callback.close(self.handle)
    uv.close(self.handle, uv_callback.close.cb)
    response.wait()
    self.closed = True
#    # Should be safe to release them here.
#    # TODO: remove this
    buffers, self.buffers = self.buffers, []
    for pointer in buffers:
        lltype.free(pointer, flavor='raw')

    lltype.free(self.handle, flavor='raw')
    self.handle = lltype.nullptr(uv.handle_ptr.TO)
    return null

@Handle.method(u"get_send_buffer_size", signature(Handle))
def Handle_get_send_buffer_size(self):
    value = lltype.malloc(rffi.INTP.TO, 1, flavor='raw', zero=True)
    try:
        check( uv.send_buffer_size(self.handle, value) )
        return Integer(rffi.r_long(value[0]))
    finally:
        lltype.free(value, flavor='raw')

@Handle.method(u"get_recv_buffer_size", signature(Handle))
def Handle_get_recv_buffer_size(self):
    value = lltype.malloc(rffi.INTP.TO, 1, flavor='raw', zero=True)
    try:
        check( uv.recv_buffer_size(self.handle, value) )
        return Integer(rffi.r_long(value[0]))
    finally:
        lltype.free(value, flavor='raw')

# TODO: uv.fileno(handle, fd) ?

def check(result):
    if rffi.r_long(result) < 0:
        raise uv_callback.to_error(result)
