{
  description = "Python dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = {self, nixpkgs}: {
    devShells.x86_64-linux.default = let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
      system = "x86_64-linux";
    in pkgs.mkShell {
      packages = with pkgs; [
        (python313.withPackages (ps: with ps; [
          pandas
          numpy
          matplotlib
          django
          psycopg2-binary
          djangorestframework
          drf-yasg
          seaborn
        ]))
      ];
      shell = pkgs.zsh;
      shellHook = ''
        export SHELL=${pkgs.zsh}/bin/zsh
        exec zsh
      '';
    };
  };
}