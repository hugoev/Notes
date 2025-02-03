'use client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getNotes, 
  createNote, 
  updateNote, 
  deleteNote, 
  togglePinNote,
  getCategories,
  createCategory,
  deleteCategory,
  type Note,
  type Category 
} from '@/services/api';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { toast } from "@/hooks/use-toast";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { motion, AnimatePresence } from "framer-motion";
import { format } from 'date-fns';
import { 
  FolderIcon, 
  PlusIcon, 
  SearchIcon, 
  ChevronDownIcon, 
  Settings2Icon,
  LayoutGridIcon,
  LayoutListIcon,
  Share2Icon,
  TrashIcon,
  PencilIcon,
  PinIcon,
  LogOutIcon,
  FolderPlusIcon,
  NotebookPen,
  ClockIcon,
  FileTextIcon,
} from 'lucide-react';
import { ThemeCustomizer } from '@/components/theme-customizer';
import { ThemeToggle } from '@/components/theme-switcher';

interface NewCategoryDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (name: string) => void;
}

const NewCategoryDialog = ({ isOpen, onClose, onConfirm }: NewCategoryDialogProps) => {
  const [categoryName, setCategoryName] = useState('');

  return (
    <AlertDialog open={isOpen} onOpenChange={onClose}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Create New Category</AlertDialogTitle>
          <Input
            placeholder="Category name"
            value={categoryName}
            onChange={(e) => setCategoryName(e.target.value)}
            className="mt-4"
          />
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={onClose}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={() => {
              if (categoryName.trim()) {
                onConfirm(categoryName);
                setCategoryName('');
              }
            }}
          >
            Create
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default function Notes() {
  // State
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [newNoteMode, setNewNoteMode] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isClient, setIsClient] = useState(false);
  const [isGridView, setIsGridView] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [noteToDelete, setNoteToDelete] = useState<Note | null>(null);
  const [newCategoryDialogOpen, setNewCategoryDialogOpen] = useState(false);

  // Hooks
  const router = useRouter();
  const { token, logout } = useAuthStore();
  const queryClient = useQueryClient();

  useEffect(() => {
    setIsClient(true);
    if (!token) {
      router.push('/login');
    }
  }, [token, router]);

  // Queries
  const { data: categories = [], isLoading: categoriesLoading } = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: getCategories,
    enabled: !!token && isClient,
  });

  const { data: notes = [], isLoading: notesLoading } = useQuery<Note[]>({
    queryKey: ['notes', selectedCategory?.id],
    queryFn: getNotes,
    enabled: !!token && isClient,
  });

  // Mutations
  const createNoteMutation = useMutation({
    mutationFn: createNote,
    onSuccess: (newNote) => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      setNewNoteMode(false);
      setSelectedNote(newNote);
      setTitle('');
      setContent('');
      toast({
        title: "Note Created",
        description: "Your note has been created successfully.",
      });
    },
  });

  const updateNoteMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: { title: string; content: string; category?: number | null } }) => 
      updateNote(id, data),
    onSuccess: (updatedNote) => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      setNewNoteMode(false);
      setSelectedNote(updatedNote);
      toast({
        title: "Note Updated",
        description: "Your note has been updated successfully.",
      });
    },
  });

  const deleteNoteMutation = useMutation({
    mutationFn: deleteNote,
    onMutate: async (deleteId) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['notes'] });
  
      // Snapshot the previous value
      const previousNotes = queryClient.getQueryData<Note[]>(['notes']);
  
      // Optimistically remove the note
      queryClient.setQueryData<Note[]>(['notes'], (old = []) => 
        old.filter(note => note.id !== deleteId)
      );
  
      return { previousNotes };
    },
    onError: (err, variables, context) => {
      // If the mutation fails, restore the previous notes
      if (context?.previousNotes) {
        queryClient.setQueryData(['notes'], context.previousNotes);
      }
      toast({
        title: "Error",
        description: "Failed to delete note",
        variant: "destructive",
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      setSelectedNote(null);
      setNoteToDelete(null);
      setDeleteDialogOpen(false);
      toast({
        title: "Note Deleted",
        description: "Note has been deleted successfully",
      });
    },
  });

  const togglePinMutation = useMutation({
    mutationFn: ({ id, isPinned }: { id: number; isPinned: boolean }) => 
      togglePinNote(id, isPinned),
    onMutate: async ({ id, isPinned }) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['notes'] });
  
      // Snapshot the previous value
      const previousNotes = queryClient.getQueryData<Note[]>(['notes']);
  
      // Optimistically update the note
      queryClient.setQueryData<Note[]>(['notes'], (old = []) => 
        old.map(note => 
          note.id === id 
            ? { ...note, is_pinned: isPinned }
            : note
        )
      );
  
      // Return a context object with the snapshotted value
      return { previousNotes };
    },
    onError: (err, variables, context) => {
      // If the mutation fails, restore the previous notes
      if (context?.previousNotes) {
        queryClient.setQueryData(['notes'], context.previousNotes);
      }
      toast({
        title: "Error",
        description: "Failed to update pin status",
        variant: "destructive",
      });
    },
    onSuccess: (updatedNote) => {
      // After success, invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      
      if (selectedNote?.id === updatedNote.id) {
        setSelectedNote(updatedNote);
      }
  
      toast({
        title: updatedNote.is_pinned ? "Note Pinned" : "Note Unpinned",
        description: updatedNote.is_pinned ? 
          "Your note has been pinned to the top." : 
          "Your note has been unpinned.",
      });
    },
  });

  const createCategoryMutation = useMutation({
    mutationFn: createCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      setNewCategoryDialogOpen(false);
      toast({
        title: "Category Created",
        description: "New category has been created successfully.",
      });
    },
  });

  const deleteCategoryMutation = useMutation({
    mutationFn: deleteCategory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
      if (selectedCategory) {
        setSelectedCategory(null);
      }
      toast({
        title: "Category Deleted",
        description: "Category has been deleted successfully.",
        variant: "destructive",
      });
    },
  });

// Event Handlers
const handleNewNote = () => {
  setNewNoteMode(true);
  setSelectedNote(null);
  setTitle('');
  setContent('');
};

const handleSave = async (e: React.FormEvent) => {
  e.preventDefault();
  if (title.trim() || content.trim()) {
    const noteData = {
      title: title.trim() || 'Untitled Note',
      content: content.trim(),
      category: selectedCategory?.id || null
    };

    if (selectedNote && newNoteMode) {
      await updateNoteMutation.mutate({
        id: selectedNote.id,
        data: noteData
      });
    } else {
      await createNoteMutation.mutate(noteData);
    }
  }
};

const handleDeleteNote = (note: Note) => {
  setNoteToDelete(note);
  setDeleteDialogOpen(true);
};

const confirmDelete = async () => {
  if (noteToDelete) {
    await deleteNoteMutation.mutateAsync(noteToDelete.id);
  }
};

const handleEditNote = (note: Note) => {
  setSelectedNote(note);
  setNewNoteMode(true);
  setTitle(note.title);
  setContent(note.content);
};

const handleTogglePin = async (note: Note) => {
  try {
    await togglePinMutation.mutateAsync({
      id: note.id,
      isPinned: !note.is_pinned
    });
  } catch (error) {
    toast({
      title: "Error",
      description: "Failed to update pin status",
      variant: "destructive",
    });
  }
};

const handleCreateCategory = async (name: string) => {
  if (name.trim()) {
    await createCategoryMutation.mutateAsync(name.trim());
  }
};

const handleDeleteCategory = async (categoryId: number) => {
  const notesInCategory = notes.filter(note => note.category === categoryId).length;
  if (notesInCategory > 0) {
    toast({
      title: "Cannot Delete Category",
      description: "Please remove all notes from this category first.",
      variant: "destructive",
    });
    return;
  }
  await deleteCategoryMutation.mutateAsync(categoryId);
};

const handleLogout = () => {
  logout();
  router.push('/login');
};

// Filters and Sorting
const filteredNotes = notes.filter(note => 
  (selectedCategory ? note.category === selectedCategory.id : true) &&
  (searchQuery ? (
    note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    note.content.toLowerCase().includes(searchQuery.toLowerCase())
  ) : true)
);

const sortedNotes = [...filteredNotes].sort((a, b) => {
  if (a.is_pinned && !b.is_pinned) return -1;
  if (!a.is_pinned && b.is_pinned) return 1;
  return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
});

if (!isClient || !token) return null;

return (
  <div className="flex h-screen bg-background/95">
    {/* Left Sidebar - Categories */}
    <div className="w-64 border-r bg-background/50 backdrop-blur-xl">
      <div className="p-5 flex flex-col h-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <NotebookPen className="h-4 w-4 text-primary" />
            </div>
            <span className="font-semibold text-lg">Notes</span>
          </div>
          <div className="flex items-center gap-2">
            <ThemeCustomizer />
            <ThemeToggle />
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-8 w-8 hover:text-red-500 transition-colors"
              onClick={handleLogout}
            >
              <LogOutIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>

    <ScrollArea className="flex-1 -mx-1 px-1">
      {/* All Notes Button */}
      <div className="space-y-1 mb-6">
        <Button
          variant={!selectedCategory ? "secondary" : "ghost"}
          className="w-full justify-start h-9 px-4 font-medium"
          onClick={() => setSelectedCategory(null)}
        >
          <FolderIcon className="h-4 w-4 mr-2 text-blue-500" />
          All Notes
          <span className="ml-auto text-xs bg-muted px-2 py-0.5 rounded-md">
            {notes.length}
          </span>
        </Button>
      </div>

      {/* Categories Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between px-2 mb-2">
          <span className="text-sm font-medium text-muted-foreground">Categories</span>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 hover:bg-accent"
            onClick={() => setNewCategoryDialogOpen(true)}
          >
            <PlusIcon className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-1">
          {categories.map((category) => (
            <div key={category.id} className="flex items-center group px-1">
              <Button
                variant={selectedCategory?.id === category.id ? "secondary" : "ghost"}
                className="flex-1 justify-start h-9 rounded-r-none border-r border-transparent"
                onClick={() => setSelectedCategory(category)}
              >
                <FolderIcon className={`h-4 w-4 mr-2 ${
                  selectedCategory?.id === category.id 
                    ? 'text-primary'
                    : 'text-muted-foreground'
                }`} />
                <span className="truncate">{category.name}</span>
                <span className="ml-auto text-xs bg-muted/60 px-2 py-0.5 rounded-md">
                  {notes.filter(note => note.category === category.id).length}
                </span>
              </Button>
              <Button
                variant={selectedCategory?.id === category.id ? "secondary" : "ghost"}
                size="sm"
                className={`h-9 px-2 rounded-l-none opacity-0 group-hover:opacity-100 
                  transition-all duration-200 hover:text-red-500 border-l border-transparent
                  ${selectedCategory?.id === category.id ? 'bg-accent' : ''}`}
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteCategory(category.id);
                }}
              >
                <TrashIcon className="h-4 w-4" />
              </Button>
            </div>
          ))}

          {categories.length === 0 && (
            <div className="px-4 py-3 text-sm text-muted-foreground text-center">
              No categories yet
            </div>
          )}
        </div>
      </div>
    </ScrollArea>

    {/* Footer */}
    <div className="mt-auto pt-4">
      <Separator className="mb-4" />
      <Button
        variant="outline"
        size="sm"
        className="w-full justify-start"
        onClick={() => setNewCategoryDialogOpen(true)}
      >
        <FolderPlusIcon className="h-4 w-4 mr-2" />
        New Category
      </Button>
    </div>
  </div>
</div>

    {/* Middle Column - Notes List */}
    <div className="w-80 border-r bg-background/50 backdrop-blur-xl flex flex-col">
      <div className="p-5 border-b">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h2 className="font-semibold text-lg">{selectedCategory?.name || 'All Notes'}</h2>
            <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-md">
              {sortedNotes.length}
            </span>
          </div>
          <div className="flex gap-1">
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-8 w-8"
              onClick={() => setIsGridView(!isGridView)}
            >
              {isGridView ? (
                <LayoutListIcon className="h-4 w-4" />
              ) : (
                <LayoutGridIcon className="h-4 w-4" />
              )}
            </Button>
            <Button 
              variant="default" 
              size="icon" 
              className="h-8 w-8"
              onClick={handleNewNote}
            >
              <PlusIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search notes..."
            className="pl-9 bg-muted/50"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Notes List */}
      <ScrollArea className="flex-1">
        <div className={`p-3 grid ${isGridView ? 'grid-cols-2 gap-2' : 'grid-cols-1 gap-1'}`}>
          <AnimatePresence>
            {sortedNotes.map((note) => (
              <motion.div
                key={note.id}
                layout
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`
                  group
                  ${isGridView 
                    ? 'rounded-lg border shadow-sm bg-background/50 hover:shadow-md' 
                    : 'border-b last:border-b-0'}
                  ${selectedNote?.id === note.id ? 'bg-accent shadow-md' : ''} 
                  hover:bg-accent/50 transition-all cursor-pointer p-3
                `}
                onClick={() => {
                  setSelectedNote(note);
                  setNewNoteMode(false);
                }}
              >
                <div className="flex flex-col gap-2">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2 min-w-0 flex-1">
                      <h3 className="font-medium truncate text-sm">
                        {note.title || 'Untitled Note'}
                      </h3>
                      {note.is_pinned && (
                        <PinIcon className="h-3 w-3 text-blue-500 flex-shrink-0" />
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground truncate">
                    {note.content || 'No additional text'}
                  </p>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>{format(new Date(note.updated_at), 'MMM d, yyyy')}</span>
                    {note.category && (
                      <>
                        <span>•</span>
                        <span className="truncate">
                          {categories.find(c => c.id === note.category)?.name}
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {sortedNotes.length === 0 && !searchQuery && (
            <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
              <div className="h-12 w-12 rounded-lg bg-muted flex items-center justify-center mb-4">
                <NotebookPen className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="font-medium text-muted-foreground mb-1">No notes yet</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Create your first note to get started
              </p>
              <Button onClick={handleNewNote} variant="outline" size="sm">
                <PlusIcon className="h-4 w-4 mr-2" />
                New Note
              </Button>
            </div>
          )}

          {sortedNotes.length === 0 && searchQuery && (
            <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
              <div className="h-12 w-12 rounded-lg bg-muted flex items-center justify-center mb-4">
                <SearchIcon className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="font-medium text-muted-foreground mb-1">No results found</h3>
              <p className="text-sm text-muted-foreground">
                No notes match your search
              </p>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>

    {/* Right Column - Note Editor */}
    <div className="flex-1 flex flex-col bg-background">
      <AnimatePresence mode="wait">
        {(selectedNote || newNoteMode) ? (
          <motion.form
            key="form"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onSubmit={handleSave}
            className="flex-1 flex flex-col"
          >
            {/* Editor Header */}
            <div className="px-8 py-6 border-b">
              <div className="flex items-center justify-between mb-4">
                <Input
                  type="text"
                  placeholder="Untitled Note"
                  value={newNoteMode ? title : selectedNote?.title || ''}
                  onChange={(e) => setTitle(e.target.value)}
                  className="text-xl font-medium border-0 p-0 focus-visible:ring-0 bg-transparent max-w-[500px]"
                  disabled={!newNoteMode}
                />
                <div className="flex items-center gap-2">
                  {selectedNote && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleTogglePin(selectedNote)}
                      type="button"
                      disabled={togglePinMutation.isPending}
                      className="hover:bg-accent"
                    >
                      <PinIcon 
                        className={`h-4 w-4 transition-colors ${
                          selectedNote.is_pinned ? 'text-blue-500' : 'text-muted-foreground'
                        }`} 
                      />
                    </Button>
                  )}
                  {!newNoteMode && (
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => selectedNote && handleEditNote(selectedNote)}
                      type="button"
                      className="hover:bg-accent"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </Button>
                  )}
                  {selectedNote && (
                    <Button 
                      variant="ghost" 
                      size="icon"
                      onClick={() => handleDeleteNote(selectedNote)}
                      type="button"
                      className="hover:bg-accent hover:text-red-500"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <ClockIcon className="h-4 w-4" />
                  <span>
                    {newNoteMode 
                      ? 'New note' 
                      : `Last edited ${format(new Date(selectedNote?.updated_at || ''), 'MMM d, yyyy h:mm a')}`
                    }
                  </span>
                </div>
                {selectedNote?.category && (
                  <div className="flex items-center gap-2">
                    <FolderIcon className="h-4 w-4" />
                    <span>{categories.find(c => c.id === selectedNote.category)?.name}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Editor Content */}
            <div className="flex-1 flex flex-col">
              <Textarea
                placeholder="Start writing..."
                value={newNoteMode ? content : selectedNote?.content || ''}
                onChange={(e) => setContent(e.target.value)}
                className="flex-1 resize-none border-0 focus-visible:ring-0 px-8 py-6 text-base leading-relaxed"
                disabled={!newNoteMode}
              />
            </div>

            {/* Editor Footer */}
            {newNoteMode && (
              <div className="px-8 py-4 border-t bg-muted/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <select 
                      className="text-sm bg-transparent border-0 text-muted-foreground"
                      value={selectedCategory?.id || ''}
                      onChange={(e) => {
                        const categoryId = parseInt(e.target.value);
                        setSelectedCategory(categories.find(c => c.id === categoryId) || null);
                      }}
                    >
                      <option value="">No Category</option>
                      {categories.map((category) => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" type="button" onClick={() => setNewNoteMode(false)}>
                      Cancel
                    </Button>
                    <Button type="submit">
                      Save Note
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </motion.form>
        ) : (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex-1 flex items-center justify-center"
          >
            <div className="text-center">
              <div className="h-16 w-16 rounded-xl bg-muted flex items-center justify-center mx-auto mb-4">
                <FileTextIcon className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-medium mb-2">No Note Selected</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Select a note from the list or create a new one
              </p>
              <Button variant="outline" onClick={handleNewNote}>
                <PlusIcon className="h-4 w-4 mr-2" />
                New Note
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>

    {/* Dialogs */}
    <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Note</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete this note? This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={deleteNoteMutation.isPending}>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={confirmDelete}
            className="bg-red-500 hover:bg-red-600 transition-colors"
            disabled={deleteNoteMutation.isPending}
          >
            {deleteNoteMutation.isPending ? "Deleting..." : "Delete"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>

    <NewCategoryDialog
      isOpen={newCategoryDialogOpen}
      onClose={() => setNewCategoryDialogOpen(false)}
      onConfirm={handleCreateCategory}
    />
  </div>
);
}