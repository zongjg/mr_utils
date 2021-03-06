'''Server to be running on network machine.

Must be running for client to be able to connect.  Obviously, alongside this
server, MATLAB should also be running.
'''

import socketserver
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
import logging
from functools import partial

from mr_utils.config import ProfileConfig
from mr_utils.matlab.contract import done_token, RUN, GET, PUT

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

class MATLAB(object):
    '''Object on server allowing server to communicate with MATLAB instance.

    Attributes
    ==========
    done_token : contract.done_token
        Sequence of symbols to let us know MATLAB is done communicating.
    process : subprocess
        Process that runs MATLAB and stays open.
    '''

    def __init__(self):

        # When we run a command we need to know when we're done...
        self.done_token = done_token

        # start instance of matlab of host
        cmd = 'matlab -nodesktop -nosplash'
        self.process = Popen(
            cmd.split(),
            stdin=PIPE, stdout=PIPE, bufsize=1, universal_newlines=True)
        self.process.stdin.write("fprintf('%s\\n')\n" % self.done_token)

        # Read out opening message
        self.catch_output()

    def run(self, cmd, log_func=None):
        '''Run MATLAB command in subprocess.

        Parameters
        ==========
        cmd : str
            Command to send to MATLAB console.
        log_func : callable, optional
            Function to use to log output of MATLAB console.
        '''

        self.process.stdin.write(('%s\n' % cmd))
        self.process.stdin.write("fprintf('%s\\n')\n" % self.done_token)
        logging.info(cmd)
        if log_func is not None:
            log_func(cmd)

        # Capture output if any from command.  There will at least be the
        # done_token to collect.
        self.catch_output(log_func=log_func)

    def catch_output(self, log_func=None):
        '''Grab the output of MATLAB on the server.

        Parameters
        ==========
        log_func : callable, optional
            Function to use to log output of MATLAB console.
        '''

        for l in self.process.stdout:
            if log_func is not None:
                log_func(l.rstrip())
            if self.done_token in l.rstrip():
                break
            logging.info(l.rstrip())

    def get(self, varnames):
        '''Get variables from MATLAB workspace into python as numpy arrays.

        Parameters
        ==========
        varnames : list
            List of names of variables in MATLAB workspace to get.

        Returns
        =======
        tmp_filename : str
            Name of temporary file where MATLAB workspace contents are stored.

        Raises
        ======
        ValueError
            When `varnames` is not a list type object.

        Notes
        =====
        Notice that varnames should be a list of strings.
        '''

        if not isinstance(varnames, list):
            try:
                varnames = list(varnames)
            except:
                raise ValueError(
                    'varnames should be a list of variable names!')

        tmp_filename = NamedTemporaryFile(suffix='.mat').name
        cmd = "save('%s',%s)" % (tmp_filename, \
            ','.join(["'%s'" % vname for vname in varnames]))
        self.run(cmd)

        return tmp_filename

    def put(self, tmp_filename):
        '''Put variables from python into MATLAB workspace.

        Parameters
        ==========
        tmp_filename : str
            MAT file holding variables to inject into workspace.
        '''

        cmd = "load('%s','-mat')" % tmp_filename
        self.run(cmd)

    def exit(self):
        '''Send exit command to MATLAB.'''

        _out, _err = self.process.communicate('exit\n')

        exit_message = 'MATLAB finished with return code \
            %d' % self.process.returncode
        if self.process.returncode == 0:
            logging.info(exit_message)
        else:
            logging.error(exit_message)


class MyTCPHandler(socketserver.StreamRequestHandler):
    '''Create the server, binding to localhost on port.

    Attributes
    ==========
    what : {contract.RUN, contract.GET, contract.PUT}
        The action we wish to perform.
    cmd : str
        The command to be run in the MATLAB console.
    rfile : stream
        Stream from TCP socket that we are reading from.
    '''

    def handle(self):

        # Incoming connection...
        logging.info('%s connected', self.client_address[0])

        # See what they want to do
        self.what = self.rfile.readline().strip().decode()
        if self.what == RUN:

            # The command will be coming next
            self.cmd = self.rfile.readline().strip()
            # logging.info('cmd issued: %s' % self.cmd.decode())
            self.server.matlab.run(
                self.cmd.decode(),
                log_func=lambda x: self.wfile.write(x.encode()))

        elif self.what == GET:

            # Client will say what the bufsize is:
            bufsize = int(self.rfile.readline().strip().decode())
            logging.info('bufsize for %s is %d', GET, bufsize)

            # The list of varnames to get from the workspace will be next
            varnames = self.rfile.readline().strip().decode()
            tmp_filename = self.server.matlab.get(varnames.split())

            # Send binary file over socket
            with open(tmp_filename, 'rb') as f:
                for chunk in iter(partial(f.read, bufsize), b''):
                    self.wfile.write(chunk)
            self.wfile.write(done_token.encode())

        elif self.what == PUT:

            # Client will say what the bufsize is:
            bufsize = int(self.rfile.readline().strip().decode())
            logging.info('bufsize for %s is %d', PUT, bufsize)

            # Get ready to recieve file
            tmp_filename = NamedTemporaryFile().name
            with open(tmp_filename, 'wb') as f:
                done = False
                while not done:
                    received = self.rfile.read(bufsize)
                    if bytes(done_token, 'utf-8') in received:
                        received = received[:-len(done_token)]
                        done = True
                    f.write(received)

            self.server.matlab.put(tmp_filename)

        else:
            msg = 'Not quite sure what you want me to do, \
                %s is not a valid identifier.' % self.what
            self.wfile.write(msg.encode())
            logging.info(msg)

def start_server():
    '''Start the server so the client can connect.

    Notes
    =====
    This server must be running on the remote before client can be used to
    connect to it.

    Examples
    ========
    To run this server, simply run:

    .. code-block:: bash

        python3 mr_utils/matlab/start_server.py
    '''

    # Find host,port from profiles.config
    profile = ProfileConfig()
    host = profile.get_config_val('matlab.host')
    port = profile.get_config_val('matlab.port')

    # Start an instance of MATLAB
    try:
        matlab = MATLAB()
        server = socketserver.TCPServer((host, port), MyTCPHandler)
        server.matlab = matlab

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        logging.info('Server running on %s:%d', host, port)
        logging.info('Interrupt the server with Ctrl-C')
        server.serve_forever()
    finally:
        logging.info('Just a sec, stopping matlab and freeing up ports...')
        matlab.exit()


if __name__ == '__main__':
    start_server()
