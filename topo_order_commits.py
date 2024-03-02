#!/usr/bin/python3

'''
Hayk Chilingaryan
COM SCI 35L
03/01/2024
'''

import os
import sys
import zlib

class CommitNode:
    def __init__(self, commit_hash_code, branch=[]):
        self.commit_hash_code = commit_hash_code
        self.parents = set()
        self.children = set()
        self.branch = branch
        
'''
git_exist() checks to find the .git folder
'''        
def git_exist():
    while os.getcwd() != '/' and '.git' not in os.listdir():
        os.chdir('../')
    return '.git' in os.listdir()

'''
git_check() throws an error if git folder doesn't exist, and exits
'''
def git_check():
    if not git_exist():
        sys.stderr.write('Not inside of a Git repository\n')
        exit(1)
    gitfold = os.path.join(os.getcwd(), '.git')
    if not os.path.isdir(gitfold):
        sys.stderr.write('Not inside of a Git repository\n')
        exit(1)
    os.chdir(gitfold)


'''
make_branchhashmap() returns a map with hascode of branch as key and branch names as values
'''
def make_branchhashmap():
    branch_map = {}
    os.chdir('./refs/heads')
    for root, dirs, files in os.walk("."):
        for name in files + dirs:
            if os.path.isfile(os.path.join(root, name)):
                branch_name = os.path.join(root, name)[2:]
                fopen = open(branch_name, 'r')
                hash_code = fopen.read()[:-1]
                if hash_code not in branch_map.keys():
                    branch_map[hash_code] = [branch_name]
                else:
                    branch_map[hash_code].append(branch_name)
                fopen.close()
    os.chdir('../../')
    return branch_map

'''
parent_hash_code gets the hash codes of the parents
'''
def parent_hash_code(det):
    parents = []
    for line in det.split('\n'):
        if line.startswith('parent'):
            parents.append(line.split(' ')[1])
    return parents

'''
get_parents gets the list of parents of a specific commit hash
'''
def get_parents(hash_code):
    h1, h2 = hash_code[0:2], hash_code[2:]
    os.chdir(os.path.join('.', h1))
    c_f = open(h2, 'rb')
    det = zlib.decompress(c_f.read()).decode()
    c_f.close()
    os.chdir('../')
    return parent_hash_code(det)

'''
make_DAG creates a DAG with the hashcodes of commits.
'''
def make_DAG(branch_map):
    os.chdir('./objects')
    node_map = {}
    root_commits = set()
    for hash_code in branch_map:
        if hash_code in node_map.keys():
            node_map[hash_code].branch = branch_map[hash_code]
        else:
            node_map[hash_code] = CommitNode(hash_code, branch_map[hash_code])
            stack = [node_map[hash_code]]
            while len(stack) != 0:
                node = stack.pop()
                parent_hash_codees = get_parents(node.commit_hash_code)
                if len(parent_hash_codees) == 0:
                    root_commits.add(node.commit_hash_code)
                for p in parent_hash_codees:
                    if p not in node_map.keys():
                        node_map[p] = CommitNode(p)
                    node.parents.add(node_map[p])
                    node_map[p].children.add(node)
                    stack.append(node_map[p])
    os.chdir('../')
    return list(root_commits), node_map

'''
topo_sort topo sorts the commits and returns a list.
'''
def topo_sort(root_commits, node_map):
    L, vis, stack = [], set(), root_commits.copy()
    while len(stack) != 0:
        top = stack[-1]
        vis.add(top)
        children = [c for c in node_map[top].children if c.commit_hash_code not in vis]
        # stop recursing if no more children
        if len(children) == 0:
            stack.pop()
            L.append(top)
        else:
            stack.append(children[0].commit_hash_code)
    return L


'''
output prints the topologically sorted list in given format.
'''
def output(topo_list, node_map):
    for i in range(len(topo_list)):
        n1 = node_map[topo_list[i]]
        if len(n1.branch) == 0:
            print(topo_list[i])
        else:
            print(topo_list[i] + " ", end="")
            print(*sorted(n1.branch))
        if i < (len(topo_list) - 1):
            n2 = node_map[topo_list[i + 1]]
            if topo_list[i + 1] not in [p.commit_hash_code for p in n1.parents]:
                print(*[p.commit_hash_code for p in n1.parents], end="=\n\n=")
                print(*[c.commit_hash_code for c in n2.children])

def topo_order_commits():
    git_check()
    branch_map = make_branchhashmap()
    root_commits, node_map = make_DAG(branch_map)
    topo_list = topo_sort(root_commits, node_map)
    output(topo_list, node_map)

if __name__ == '__main__':
    topo_order_commits()
    
'''
By running strace -f python3 topo_order_commits.py, made sure no external commands were used and called and my commands used python recognized commands only
'''
