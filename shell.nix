with (import <nixpkgs> {});
mkShell {
  buildInputs = with pkgs; [
    python311
    python311Packages.beautifulsoup4
    python311Packages.requests
  ];
}
