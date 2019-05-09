import interface
reload(interface)

def start():
    main_shelf_window = interface.mainShelfWindow('mainShelfWindow','Tool',True)
    main_shelf_window.run()