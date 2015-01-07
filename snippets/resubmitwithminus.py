import subprocess
import time

cmd_file = 'command_list.txt'
is_test = False
sleepytime = 0.5
f = open(cmd_file, 'r')
alllines = f.readlines()
f.close()


def fix_angle(rawline):
    """
    takes the executed argument, finds the angle argument
    if it is greater than 0 it is inversed and then a new
    command to execute is returned, otherwise empty "" is returned
    """
    inline = rawline.split(' ')
    # get angle argument
    ang_args = filter(lambda x: x[1] == '-a', enumerate(inline))
    if len(ang_args) > 0:
        ang_arg = ang_args[0]
        # get angle value
        ang_val = float(inline[ang_arg[0] + 1])
        if abs(ang_val) > 0.01:
            ang_val *= -1
            print (
                'Angle ', inline[ang_arg[0]:ang_arg[0] + 2],
                'has been flipped to:',
                ang_val)
            inline[ang_arg[0] + 1] = str(ang_val)
            return ' '.join(inline)
    return ''


for cline in alllines:
    new_cmd = fix_angle(cline)
    if len(new_cmd) > 0:
        print ('Submitting:', new_cmd)
        if not is_test:
            subprocess.call(new_cmd, shell=True)
            time.sleep(sleepytime)
