from data_utils import generic_shell

command1=generic_shell("touch temp1","./generic-shell.txt")
command1=generic_shell("touch temp2","./generic-shell.txt")
command4=generic_shell("echo 'abc' >> ./temp1","./generic-shell.txt")
command5=generic_shell("echo temp2 >> temp2","./generic-shell.txt")
command3=generic_shell("paste temp1 temp2 > temp3" , "./generic-shell.txt")