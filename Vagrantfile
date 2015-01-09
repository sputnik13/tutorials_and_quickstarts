# -*- mode: ruby -*-
# # vi: set ft=ruby :

require 'fileutils'

Vagrant.require_version ">= 1.6.0"

CONFIG = File.join(File.dirname(__FILE__), "vagrant_config.rb")

VAGRANTFILE_API_VERSION = "2"

# Defaults for config options
$hostname = File.basename(File.dirname(__FILE__))
$forwarded_port = 8795
$install_devstack = false
$install_build_deps = true
$install_tmate = false
$vm_memory = 2048
$vm_cpus = 2

if File.exist?(CONFIG)
  require CONFIG
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = $hostname
  config.vm.network "forwarded_port", guest: $forwarded_port, host: $forwarded_port

  config.vm.provider "virtualbox" do |v|
    v.memory = $vm_memory
    v.cpus = $vm_cpus
  end

  config.vm.provider "vmware_fusion" do |v, override|
    v.vmx["memsize"] = $vm_memory
    v.vmx["numvcpus"] = $vm_cpus
    override.vm.box = "puphpet/ubuntu1404-x64"
  end

  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  # Update package list first and ensure package/repository management tools are present
  config.vm.provision "shell", inline: "sudo apt-get update"
  config.vm.provision "shell", inline: "sudo apt-get install -y python-software-properties software-properties-common"

end
