class Version( object ):

    def __init__( self ):
        self.MajorVersionNumber = 1
        self.MinorVersionNumber = 7
        self.BuildNumber = 0
    
    def getVersionNumber( self ):
        return str( self.MajorVersionNumber ) + '.' + str( self.MinorVersionNumber )
    
    def getVerboseVersionNumber( self ):
        return str( self.MajorVersionNumber ) + '.' + str( self.MinorVersionNumber ) + '.' + str( self.BuildNumber )
    
    def getBuildNumber( self ):
        return str( self.BuildNumber )