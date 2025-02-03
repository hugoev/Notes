"use client"

import * as React from "react"
import { Paintbrush } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

type ThemeProperties = {
  [key: string]: string;
}

interface ThemeOption {
  name: string;
  value: string;
  properties: {
    light: ThemeProperties;
    dark: ThemeProperties;
  };
}

const themes: ThemeOption[] = [
  {
    name: "Zinc",
    value: "zinc",
    properties: {
      light: {
        "--background": "0 0% 100%",
        "--foreground": "240 5.9% 10%",
        "--card": "0 0% 100%",
        "--card-foreground": "240 5.9% 10%",
        "--popover": "0 0% 100%",
        "--popover-foreground": "240 5.9% 10%",
        "--primary": "240 5.9% 10%",
        "--primary-foreground": "0 0% 98%",
        "--secondary": "240 4.8% 95.9%",
        "--secondary-foreground": "240 5.9% 10%",
        "--muted": "240 4.8% 95.9%",
        "--muted-foreground": "240 3.8% 46.1%",
        "--accent": "240 4.8% 95.9%",
        "--accent-foreground": "240 5.9% 10%",
        "--destructive": "0 84.2% 60.2%",
        "--destructive-foreground": "0 0% 98%",
        "--border": "240 5.9% 90%",
        "--input": "240 5.9% 90%",
        "--ring": "240 5.9% 10%",
      },
      dark: {
        "--background": "240 10% 3.9%",
        "--foreground": "0 0% 98%",
        "--card": "240 10% 3.9%",
        "--card-foreground": "0 0% 98%",
        "--popover": "240 10% 3.9%",
        "--popover-foreground": "0 0% 98%",
        "--primary": "0 0% 98%",
        "--primary-foreground": "240 5.9% 10%",
        "--secondary": "240 3.7% 15.9%",
        "--secondary-foreground": "0 0% 98%",
        "--muted": "240 3.7% 15.9%",
        "--muted-foreground": "240 5% 64.9%",
        "--accent": "240 3.7% 15.9%",
        "--accent-foreground": "0 0% 98%",
        "--destructive": "0 62.8% 30.6%",
        "--destructive-foreground": "0 0% 98%",
        "--border": "240 3.7% 15.9%",
        "--input": "240 3.7% 15.9%",
        "--ring": "240 4.9% 83.9%",
      },
    },
  },
  {
    name: "Rose",
    value: "rose",
    properties: {
      light: {
        "--background": "0 0% 100%",
        "--foreground": "240 5.9% 10%",
        "--card": "0 0% 100%",
        "--card-foreground": "240 5.9% 10%",
        "--popover": "0 0% 100%",
        "--popover-foreground": "240 5.9% 10%",
        "--primary": "346.8 77.2% 49.8%",
        "--primary-foreground": "355.7 100% 97.3%",
        "--secondary": "346.8 77.2% 96.1%",
        "--secondary-foreground": "346.8 77.2% 11.2%",
        "--muted": "346.8 77.2% 96.1%",
        "--muted-foreground": "346.8 77.2% 46.9%",
        "--accent": "346.8 77.2% 96.1%",
        "--accent-foreground": "346.8 77.2% 11.2%",
        "--destructive": "0 84.2% 60.2%",
        "--destructive-foreground": "0 0% 98%",
        "--border": "346.8 77.2% 91.4%",
        "--input": "346.8 77.2% 91.4%",
        "--ring": "346.8 77.2% 49.8%",
      },
      dark: {
        "--background": "20 14.3% 4.1%",
        "--foreground": "0 0% 95%",
        "--card": "24 9.8% 10%",
        "--card-foreground": "0 0% 95%",
        "--popover": "0 0% 9%",
        "--popover-foreground": "0 0% 95%",
        "--primary": "346.8 77.2% 49.8%",
        "--primary-foreground": "355.7 100% 97.3%",
        "--secondary": "346.8 77.2% 15.9%",
        "--secondary-foreground": "346.8 77.2% 95.9%",
        "--muted": "346.8 77.2% 15.9%",
        "--muted-foreground": "346.8 77.2% 63.9%",
        "--accent": "346.8 77.2% 15.9%",
        "--accent-foreground": "346.8 77.2% 95.9%",
        "--destructive": "0 62.8% 30.6%",
        "--destructive-foreground": "0 0% 98%",
        "--border": "346.8 77.2% 15.9%",
        "--input": "346.8 77.2% 15.9%",
        "--ring": "346.8 77.2% 49.8%",
      },
    },
  },
  {
    name: "Blue",
    value: "blue",
    properties: {
      light: {
        "--background": "0 0% 100%",
        "--foreground": "222.2 84% 4.9%",
        "--card": "0 0% 100%",
        "--card-foreground": "222.2 84% 4.9%",
        "--popover": "0 0% 100%",
        "--popover-foreground": "222.2 84% 4.9%",
        "--primary": "221.2 83.2% 53.3%",
        "--primary-foreground": "210 40% 98%",
        "--secondary": "210 40% 96.1%",
        "--secondary-foreground": "222.2 47.4% 11.2%",
        "--muted": "210 40% 96.1%",
        "--muted-foreground": "215.4 16.3% 46.9%",
        "--accent": "210 40% 96.1%",
        "--accent-foreground": "222.2 47.4% 11.2%",
        "--destructive": "0 84.2% 60.2%",
        "--destructive-foreground": "210 40% 98%",
        "--border": "214.3 31.8% 91.4%",
        "--input": "214.3 31.8% 91.4%",
        "--ring": "221.2 83.2% 53.3%",
      },
      dark: {
        "--background": "222.2 84% 4.9%",
        "--foreground": "210 40% 98%",
        "--card": "222.2 84% 4.9%",
        "--card-foreground": "210 40% 98%",
        "--popover": "222.2 84% 4.9%",
        "--popover-foreground": "210 40% 98%",
        "--primary": "217.2 91.2% 59.8%",
        "--primary-foreground": "222.2 47.4% 11.2%",
        "--secondary": "217.2 32.6% 17.5%",
        "--secondary-foreground": "210 40% 98%",
        "--muted": "217.2 32.6% 17.5%",
        "--muted-foreground": "215 20.2% 65.1%",
        "--accent": "217.2 32.6% 17.5%",
        "--accent-foreground": "210 40% 98%",
        "--destructive": "0 62.8% 30.6%",
        "--destructive-foreground": "210 40% 98%",
        "--border": "217.2 32.6% 17.5%",
        "--input": "217.2 32.6% 17.5%",
        "--ring": "224.3 76.3% 48%",
      },
    },
  },
  {
    name: "Pink",
    value: "pink",
    properties: {
      light: {
        "--background": "0 0% 100%",
        "--foreground": "338 77% 10%",
        "--card": "0 0% 100%",
        "--card-foreground": "338 77% 10%",
        "--popover": "0 0% 100%",
        "--popover-foreground": "338 77% 10%",
        "--primary": "338 77% 86%",
        "--primary-foreground": "338 77% 10%",
        "--secondary": "338 77% 96%",
        "--secondary-foreground": "338 77% 10%",
        "--muted": "338 77% 96%",
        "--muted-foreground": "338 7% 40%",
        "--accent": "338 77% 96%",
        "--accent-foreground": "338 77% 10%",
        "--destructive": "0 84.2% 60.2%",
        "--destructive-foreground": "0 0% 98%",
        "--border": "338 77% 92%",
        "--input": "338 77% 92%",
        "--ring": "338 77% 86%",
      },
      dark: {
        "--background": "338 77% 5%",
        "--foreground": "338 77% 95%",
        "--card": "338 77% 5%",
        "--card-foreground": "338 77% 95%",
        "--popover": "338 77% 5%",
        "--popover-foreground": "338 77% 95%",
        "--primary": "338 77% 76%",
        "--primary-foreground": "338 77% 100%",
        "--secondary": "338 77% 15%",
        "--secondary-foreground": "338 77% 90%",
        "--muted": "338 77% 15%",
        "--muted-foreground": "338 7% 70%",
        "--accent": "338 77% 15%",
        "--accent-foreground": "338 77% 90%",
        "--destructive": "0 62.8% 30.6%",
        "--destructive-foreground": "0 0% 98%",
        "--border": "338 77% 25%",
        "--input": "338 77% 25%",
        "--ring": "338 77% 76%",
      },
    },
  },
];

export function ThemeCustomizer() {
  const [currentTheme, setCurrentTheme] = React.useState<string>("blue")
  const { theme: mode, setTheme } = useTheme()

  const changeTheme = (themeName: string) => {
    const theme = themes.find((t) => t.value === themeName)
    if (theme) {
      const root = document.documentElement
      const properties = mode === 'dark' ? theme.properties.dark : theme.properties.light
      Object.entries(properties).forEach(([property, value]) => {
        root.style.setProperty(property, value)
      })
      setCurrentTheme(themeName)
      localStorage.setItem("app-theme", themeName)
    }
  }

  React.useEffect(() => {
    const savedTheme = localStorage.getItem("app-theme")
    if (savedTheme && themes.some((t) => t.value === savedTheme)) {
      changeTheme(savedTheme)
    }
  }, [mode])

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <Paintbrush className="h-4 w-4" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40">
        {themes.map(({ name, value, properties }) => {
          const themeProperties = mode === 'dark' ? properties.dark : properties.light;
          return (
            <DropdownMenuItem
              key={value}
              onClick={() => changeTheme(value)}
              className="flex items-center justify-between"
            >
              <div className="flex items-center gap-2">
                <div
                  className="h-4 w-4 rounded-full"
                  style={{ backgroundColor: `hsl(${themeProperties["--primary"]})` }}
                />
                <span className={currentTheme === value ? "font-medium" : ""}>
                  {name}
                </span>
              </div>
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}